@REM # catania_stat_test.sh -- Secure Request to Catania Statistics API 

@REM # This is the original script provided by Oleg with one change: 
@REM #   The final curl does not write to a file but returns the result JSON to STDOUT
@REM #   The Python subprocess result.stdout will contain the JSON payload from the API request

@REM # Step 1: Set the URL and credentials
@REM # TOKEN_URL="https://is.trltm.ostrava.corp.telstra.com/oauth2/token"
@REM # GRANT_TYPE="c########s"
@REM # AUTH_HEADER="Authorization: ##### ################################################"
 
@REM # # Step 2: Get the token
@REM # # RESPONSE=$(curl -k -X POST $TOKEN_URL -d "grant_type=$GRANT_TYPE" -H "$AUTH_HEADER")
 
@REM # # Extract the access_token and token_type from the respone
@REM # ACCESS_TOKEN=$(echo $RESPONSE | jq -r '.access_token')
@REM # TOKEN_TYPE=$(echo $RESPONSE | jq -r '.token_type')
 
@REM # # Step 3: Form the Authorization header for the health API request
@REM # AUTH_TOKEN="$TOKEN_TYPE $ACCESS_TOKEN"
 
@REM # Step 4: Make the request to the Statistics API. Output will be response from executing this script
@REM # curl -kv  https://api.gtm.ostrava.corp.telstra.com/t/catania.api/zabbix/catania/v1/statistics-service/stats -H "Source-System-Id: ZABBIX" -H "Authorization: $AUTH_TOKEN" -o temp.json
curl -s http://127.0.0.1:5000/stats/api/v1.0/test?offset=5 -o temp.json

