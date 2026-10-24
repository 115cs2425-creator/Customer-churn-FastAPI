{
    "repository": {
        "repositoryArn": "arn:aws:ecr:ap-south-1:850919910474:repository/customer-churn-app",
        "registryId": "850919910474",
        "repositoryName": "customer-churn-app",
        "repositoryUri": "850919910474.dkr.ecr.ap-south-1.amazonaws.com/customer-churn-app",
        "createdAt": "2026-10-24T02:23:54.974000+00:00",
        "imageTagMutability": "MUTABLE",
        "imageScanningConfiguration": {
            "scanOnPush": false
        },
        "encryptionConfiguration": {
            "encryptionType": "AES256"
        }
    }
}
