# Basic
A basic standard flow that calls azure open ai with Azure OpenAI connection info stored in environment variables. 

Tools used in this flow：
- `prompt` tool
- custom `python` Tool

Connections used in this flow:
- None

## Prerequisites

Install prompt-flow sdk and other dependencies:
```bash
pip install -r requirements.txt
```

## Run flow in local

- Setup environment variables
Ensure you have put your azure open ai endpoint key in [.env](.env) file. You can create one refer to this [example file](.env.example).
```bash
cat .env
```

- Test with single line data
```bash
# test with default input value in flow.dag.yaml
pf flow test --flow .
```

- Create run with multiple lines data
```bash
# using environment from .env file (loaded in user code: hello.py)
pf run create --flow . --data ./data.jsonl --stream
```

- List and show run meta
```bash
# list created run
pf run list

# show specific run detail
pf run show --name "basic_default_20230724_155834_331725"

# show output
pf run show-details --name "basic_default_20230724_155834_331725"

# visualize run in browser
pf run visualize --name "basic_default_20230724_155834_331725"
```

## Run flow locally with connection
Storing connection info in .env with plaintext is not safe. We recommend to use `pf connection` to guard secrets like `api_key` from leak.

- Show or create `azure_open_ai_connection`
```bash
# check if connection exists
pf connection show -n azure_open_ai_connection

# create connection from `azure_openai.yml` file
# Override keys with --set to avoid yaml file changes
pf connection create --file azure_openai.yml --set api_key=<your_api_key> api_base=<your_api_base>
```

- Test using connection secret specified in environment variables
```bash
# test with default input value in flow.dag.yaml 
pf flow test --flow . --environment-variables AZURE_OPENAI_API_KEY='${azure_open_ai_connection.api_key}' AZURE_OPENAI_API_BASE='${azure_open_ai_connection.api_base}'
```

- Create run using connection secret binding specified in environment variables, see [run.yml](run.yml)
```bash
# create run
pf run create --flow . --data ./data.jsonl --stream --environment-variables AZURE_OPENAI_API_KEY='${azure_open_ai_connection.api_key}' AZURE_OPENAI_API_BASE='${azure_open_ai_connection.api_base}'
# create run using yaml file
pfazure run create --file run.yml --stream

# show outputs
pf run show-details --name "basic_default_20230724_160138_517171"
```

## Run flow in cloud with connection
- Assume we already have a connection named `azure_open_ai_connection` in workspace.
```bash
# set default workspace
az account set -s 96aede12-2f73-41cb-b983-6d11a904839b
az configure --defaults group="promptflow" workspace="promptflow-eastus"
```

- Create run
```bash
# run with environment variable reference connection in azureml workspace 
pfazure run create --flow . --data ./data.jsonl --environment-variables AZURE_OPENAI_API_KEY='${azure_open_ai_connection.api_key}' AZURE_OPENAI_API_BASE='${azure_open_ai_connection.api_base}' --stream --runtime demo-mir
# run using yaml file
pfazure run create --file run.yml --stream --runtime demo-mir
```

- List and show run meta
```bash
# list created run
pfazure run list -r 3

# show specific run detail
pfazure run show --name "basic_default_20230724_160252_071554"

# show output
pfazure run show-details --name "basic_default_20230724_160252_071554"

# visualize run in browser
pfazure run visualize --name "basic_default_20230724_160252_071554"
```