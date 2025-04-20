# Clean and create fresh build dir
rm -rf localstack_api/lambda/build
mkdir -p localstack_api/lambda/build

# Install requests into the build directory
pip install requests -t localstack_api/lambda/build

# Copy the lambda function
cp localstack_api/lambda/lambda_function.py localstack_api/lambda/build/

# Zip the contents (must zip *contents* of build dir, not the dir itself)
cd localstack_api/lambda/build
zip -r ../lambda_function_payload.zip .
cd ../../../

# Redeploy
./localstack_api/deploy_llm_api.sh

