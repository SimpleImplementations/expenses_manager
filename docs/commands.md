# Deploy `.env_prod` via SCP

```bash
scp -i ~/.ssh/telegram-bot-key.pem \
  /home/prouser/repositories/money_manager/.env_prod \
  ec2-user@3.23.129.217:/home/ec2-user/expenses_manager/.env_prod
```

# Deploy in deb

ngrok http 8080

# ssh EC2
ssh -i ~/.ssh/telegram-bot-key.pem ec2-user@3.23.129.217
