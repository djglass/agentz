# LocalStack Tofu LLM API

This repo contains a fully local, serverless API stack powered by:

- ✅ [LocalStack](https://localstack.cloud/) (emulated AWS services)
- ✅ [OpenTofu](https://opentofu.org/) (open-source Terraform)
- ✅ [AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html) (locally deployed)
- ✅ [Ollama](https://ollama.com) (serving Llama3 or any local LLM)

### 🔧 Setup

1. Start [Ollama](https://ollama.com) and pull a model:

   ```bash
   ollama serve &
   ollama pull llama3

