import json

# import/export migration file names
in_file = 'exported.json'
out_file = 'genesis.json'

genesis_time = '2023-03-13T15:45:00Z'

# Load genesis
with open(in_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Update chain ID
data['chain_id'] = 'pandora-8'

# Update genesis time (https://www.mintscan.io/ixo/blocks/1254500)
data['genesis_time'] = genesis_time

# Update initial height
data['initial_height'] = '1'

# Update token module params and fields
tokenMinters = data['app_state']['token'].get('tokenMinters', [])
data['app_state']['token'] = {
    "params": {
        "ixo1155ContractCode": "2"
    },
    "tokens": tokenMinters,
    "token_properties": []
}

# Update wasm params, "addresses" was left out before and sequences values was missing
data['app_state']['wasm']['params']['code_upload_access']['addresses'] = []
data['app_state']['wasm']['sequences'] = [
    {"id_key": "BGxhc3RDb2RlSWQ=", "value": "1"},
    {"id_key": "BGxhc3RDb250cmFjdElk", "value": "1"}
]

# Update entities params and field name, createSequence new and names changed
entity_docs = data['app_state']['entity'].get('entity_docs', [])
data['app_state']['entity'] = {
    "entities": entity_docs,
    "params": {
        "createSequence": "0",
        "nftContractAddress": "ixo14hj2tavq8fpesdwxxcu44rty3hh90vhujrvcmstl4zr3txmfvw9sqa3vn7",
        "nftContractMinter": "ixo1g7xtrvc8ejkenee8a3gryvx6d4n9uu6gpsx63z"
    }
}

# Remove iid meta field as meta data now part of iid_docs
del data['app_state']['iid']['iid_meta']

# Update iid docs, add metadata and linkedClaim
for index, did in enumerate(data['app_state']['iid'].get('iid_docs', [])):
    iid = {
        **did,
        "linkedClaim": [],
        "metadata": {
            "created": genesis_time,
            "deactivated": False,
            "updated": genesis_time,
            "versionId": "1"
        },
    }
    data['app_state']['iid']['iid_docs'][index] = iid

# Add feegrant allowances
feegrant_allowances = data['app_state'].get(
    'feegrant', {}).get('allowances', [])
data['app_state']['feegrant'] = {
    "allowances": feegrant_allowances
}

# Add feeibc
data['app_state']['feeibc'] = {
    "fee_enabled_channels": [],
    "forward_relayers": [],
    "identified_fees": [],
    "registered_counterparty_payees": [],
    "registered_payees": []
}

# Add claims
data['app_state']['claims'] = {
    "claims": [],
    "collections": [],
    "disputes": [],
    "params": {
        "collection_sequence": "1",
        "ixo_account": "ixo1kqmtxkggcqa9u34lnr6shy0euvclgatw4f9zz5",
        "network_fee_percentage": "10.000000000000000000",
        "node_fee_percentage": "10.000000000000000000"
    }
}

# Add interchainaccounts
data['app_state']['interchainaccounts'] = {
    "controller_genesis_state": {
        "active_channels": [],
        "interchain_accounts": [],
        "params": {
            "controller_enabled": True
        },
        "ports": []
    },
    "host_genesis_state": {
        "active_channels": [],
        "interchain_accounts": [],
        "params": {
            "allow_messages": [
                "/cosmos.bank.v1beta1.MsgSend", "/cosmos.bank.v1beta1.MsgMultiSend",
                "/cosmos.distribution.v1beta1.MsgSetWithdrawAddress", "/cosmos.distribution.v1beta1.MsgWithdrawDelegatorReward",
                "/cosmos.gov.v1beta1.MsgVote", "/cosmos.gov.v1beta1.MsgVoteWeighted",
                "/cosmos.staking.v1beta1.MsgDelegate", "/cosmos.staking.v1beta1.MsgUndelegate", "/cosmos.staking.v1beta1.MsgBeginRedelegate",
                "/ibc.applications.transfer.v1.MsgTransfer"
            ],
            "host_enabled": True
        },
        "port": "icahost"
    }
}

# Add intertx
data['app_state']['intertx'] = None

# Update max_gas per block for wasm contracts safety
data['consensus_params']['block']["max_gas"] = "50000000"

# Remove ibc client upgrade proposal plan so chain doesnt halt again at block height
for index, proposal in enumerate(data['app_state']['gov'].get('proposals', [])):
    if proposal["content"]["@type"] == "/ibc.core.client.v1.UpgradeProposal":
        data['app_state']['gov']['proposals'][index]['content']['plan']['height'] = "0"


# Remove projects from genesis as module removed, new entities should be created
del data['app_state']['project']

# Remove payments from genesis as module removed
del data['app_state']['payments']

# Finishing touches (replace & with unicode)
data = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False)
data = data.replace('&', '\\u0026')

# Output migrated genesis
with open(out_file, 'w', encoding='utf-8') as f:
    f.write(data)
