import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

const CONTRACT = "contracts/SemanticResourceMutex.py";
const BRADBURY = { id: 4221, name: "Genlayer Bradbury Testnet", rpc: "https://rpc-bradbury.genlayer.com" };
const METHODS = ["get_policy", "get_action_count", "get_action", "has_active_lease", "get_queue", "get_active_leases", "get_event_count", "get_event", "get_authorization_event_count", "get_authorization_event", "is_requester_authorized", "set_requester_authorization", "request_lease", "renew_lease", "release_lease", "cancel_queued", "sweep_expired"];
const registry = [
  { id: "ORDER_LEDGER", label: "Order ledger", description: "The authoritative collection of purchase orders and their lifecycle states." },
  { id: "WAREHOUSE_STOCK", label: "Warehouse stock", description: "Current sellable inventory quantities reserved and held by the warehouse." },
];
const ARGS = [JSON.stringify(registry), 4, 4, 1800];
const json = (value) => JSON.stringify(value, (_key, item) => typeof item === "bigint" ? item.toString() : item, 2);
const named = (value, names) => typeof value === "string" ? value : names[Number(value)];
const executionSucceeded = (value) => ["FINISHED_WITH_RETURN", "SUCCESS"].includes(named(value, { 1: "FINISHED_WITH_RETURN" }));

function assertReceipt(receipt) {
  const status = named(receipt?.statusName ?? receipt?.status_name ?? receipt?.status, { 7: "FINALIZED" });
  const result = named(receipt?.resultName ?? receipt?.result_name ?? receipt?.result, { 1: "AGREE", 6: "MAJORITY_AGREE" });
  const execution = receipt?.txExecutionResultName ?? receipt?.tx_execution_result_name ?? receipt?.txExecutionResult ?? receipt?.consensus_data?.leader_receipt?.[0]?.execution_result;
  if (status !== "FINALIZED" || !["AGREE", "MAJORITY_AGREE"].includes(result) || !executionSucceeded(execution)) throw new Error(`Deployment did not finalize successfully: ${json(receipt)}`);
}

function deployedAddress(receipt) {
  const value = receipt?.data?.contract_address ?? receipt?.txDataDecoded?.contractAddress ?? receipt?.tx_data_decoded?.contract_address;
  if (!/^0x[0-9a-fA-F]{40}$/.test(value ?? "")) throw new Error(`Missing contract address: ${json(receipt)}`);
  return value;
}

async function retry(label, operation) {
  let last;
  for (let attempt = 0; attempt < 30; attempt += 1) {
    try { return await operation(); } catch (error) { last = error; }
    await new Promise((resolve) => setTimeout(resolve, 5000));
  }
  throw new Error(`${label} failed: ${last}`);
}

function writeArtifact(result) {
  const configured = process.env.GENLAYER_DEPLOYMENT_OUTPUT?.trim();
  if (!configured) return;
  const output = path.resolve(process.cwd(), configured);
  const root = path.resolve(process.cwd(), ".artifacts");
  if (!output.startsWith(`${root}${path.sep}`) || path.extname(output) !== ".json") throw new Error("GENLAYER_DEPLOYMENT_OUTPUT must be a JSON file under .artifacts/");
  if (existsSync(output)) throw new Error(`Refusing to overwrite ${output}`);
  mkdirSync(path.dirname(output), { recursive: true });
  writeFileSync(output, `${json(result)}\n`, "utf8");
}

export default async function deploy(client) {
  const rpc = String(client.chain?.rpcUrls?.default?.http?.[0] ?? "").replace(/\/$/, "");
  if (Number(client.chain?.id) !== BRADBURY.id || client.chain?.name !== BRADBURY.name || rpc !== BRADBURY.rpc) throw new Error(`Refusing deployment to ${client.chain?.name}/${client.chain?.id}/${rpc}`);
  const code = readFileSync(path.resolve(process.cwd(), CONTRACT), "utf8");
  const sourceBytes = Buffer.byteLength(code, "utf8");
  const deploymentInputBytes = sourceBytes + Buffer.byteLength(JSON.stringify(ARGS), "utf8");
  if (!code.trim() || deploymentInputBytes > 50000) throw new Error(`Nonportable deployment input: ${deploymentInputBytes} bytes`);
  await client.initializeConsensusSmartContract();
  const transaction = await client.deployContract({ code, args: ARGS, leaderOnly: false });
  const receipt = await client.waitForTransactionReceipt({ hash: transaction, status: "FINALIZED", retries: 720, interval: 5000 });
  assertReceipt(receipt);
  const address = deployedAddress(receipt);
  const deployed = await retry("source readback", () => client.getContractCode(address));
  if (deployed !== code) throw new Error("Deployed source differs byte-for-byte");
  const schema = await retry("schema readback", () => client.getContractSchema(address));
  for (const method of METHODS) if (!schema?.methods?.[method]) throw new Error(`Missing ABI method ${method}`);
  const policy = await client.readContract({ address, functionName: "get_policy", args: [], jsonSafeReturn: true, transactionHashVariant: "latest-final" });
  const result = { network: "bradbury", address, deployment_transaction: transaction, source_sha256: createHash("sha256").update(code, "utf8").digest("hex"), source_bytes: sourceBytes, deployment_input_bytes: deploymentInputBytes, source_exact_match: true, constructor_args: ARGS, policy, receipt };
  writeArtifact(result);
  console.log(`DEPLOYMENT_RESULT=${json(result)}`);
}
