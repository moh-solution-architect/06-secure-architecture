# 🔐 Secure Architecture — Zero Trust on AWS

![AWS](https://img.shields.io/badge/AWS-Security-FF9900?style=for-the-badge&logo=amazon-aws)
![KMS](https://img.shields.io/badge/KMS-Encryption-232F3E?style=for-the-badge&logo=amazon-aws)
![IAM](https://img.shields.io/badge/IAM-Least_Privilege-FF4F8B?style=for-the-badge&logo=amazon-aws)

Production-ready security patterns every Senior SA must know — KMS encryption, Secrets Manager, and IAM least privilege working together.

---

## 🛡️ The Security Triangle

```
        🔑 KMS
       (encrypt data)
           │
     ┌─────┴─────┐
     │           │
  🗝️ Secrets   👮 IAM
  Manager    Least Privilege
 (hide creds) (limit access)
```

---

## 🔑 Part 1 — KMS Encryption

```python
# Sensitive data BEFORE encryption
card_number = "4532-1234-5678-9012"

# AFTER KMS encryption
encrypted = "YWJlODFlM2MtOGJlZS00N2Q2..."

# Even if DB is stolen → attacker reads nothing ✅
```

**When to use:** credit cards, medical records, PII data, any regulated data

---

## 🗝️ Part 2 — Secrets Manager

```python
# ❌ WRONG — never hardcode credentials
password = "MyStr0ng!Pass#2026"

# ✅ RIGHT — fetch at runtime, never in code
secret = secrets_client.get_secret_value(SecretId='prod/myapp/database')
```

**Benefits:**
- Automatic secret rotation every 30/60/90 days
- Full audit trail — who accessed what and when
- Zero credentials in source code or environment variables

---

## 👮 Part 3 — IAM Least Privilege

```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject"],
  "Resource": "arn:aws:s3:::my-bucket/uploads/*"
}
```

**Rule:** every service gets ONLY what it needs — nothing more

| Service | Can Do | Cannot Do |
|---------|--------|-----------|
| Lambda | Read S3, Write DynamoDB | Delete, Admin |
| EC2 | Read Secrets | Access other accounts |
| Firehose | Write S3 | Read, Delete |

---

## 🚀 Run Locally

```bash
docker run -d --name localstack -p 4566:4566 localstack/localstack:3.8.1

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

python3 security_demo.py
```

---

## 📂 Structure

```
06-secure-architecture/
├── security_demo.py   # KMS + Secrets Manager + IAM demo
└── README.md
```

---

*These three patterns prevent 90% of cloud security breaches.*
