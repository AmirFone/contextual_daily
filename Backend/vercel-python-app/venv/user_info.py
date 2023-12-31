import boto3


def get_cognito_user_id(access_token, region_name="your_region"):
    """
    Retrieve the Cognito User ID for the current user.

    :param access_token: The access token of the current authenticated user.
    :param region_name: AWS region where the Cognito User Pool is located.
    :return: Cognito User ID (sub) or None if not found.
    """
    try:
        # Initialize the Cognito identity provider client
        client = boto3.client("cognito-idp", region_name=region_name)

        # Call the get_user method with the access token
        response = client.get_user(AccessToken=access_token)

        # Extract the Cognito User ID (sub)
        for attribute in response["UserAttributes"]:
            if attribute["Name"] == "sub":
                return attribute["Value"]
    except Exception as e:
        print(f"Error fetching Cognito User ID: {e}")
        return None

    return None
