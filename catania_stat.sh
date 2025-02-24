# catania_stat.sh -- Secure Request to Catania Statistics API 

# This is the original script provided by Oleg with output to local file 'temp.json' for input processing by script

# Step 1: Set the URL and credentials
TOKEN_URL="https://is.trltm.ostrava.corp.telstra.com/oauth2/token"
GRANT_TYPE="c########s"
AUTH_HEADER="Authorization: ##### ################################################"
 
# Step 2: Get the token
RESPONSE=$(curl -k -X POST $TOKEN_URL -d "grant_type=$GRANT_TYPE" -H "$AUTH_HEADER")
 
# Extract the access_token and token_type from the respone
ACCESS_TOKEN=$(echo $RESPONSE | jq -r '.access_token')
TOKEN_TYPE=$(echo $RESPONSE | jq -r '.token_type')
 
# Step 3: Form the Authorization header for the health API request
AUTH_TOKEN="$TOKEN_TYPE $ACCESS_TOKEN"
 
# Step 4: Make the request to the Statistics API. Output will be response from executing this script
curl -kv  https://api.gtm.ostrava.corp.telstra.com/t/catania.api/zabbix/catania/v1/statistics-service/stats -H "Source-System-Id: ZABBIX" -H "Authorization: $AUTH_TOKEN" -o temp.json