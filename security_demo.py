"""
Security Architecture Demo
3 مبادئ أمنية أساسية كل Senior SA لازم يعرفها
"""
import boto3, json, base64

AWS = dict(endpoint_url='http://localhost:4566',
           aws_access_key_id='test',
           aws_secret_access_key='test',
           region_name='us-east-1')

kms     = boto3.client('kms',            **AWS)
secrets = boto3.client('secretsmanager', **AWS)
iam     = boto3.client('iam',            **AWS)
s3      = boto3.client('s3',             **AWS)

print("🔐 Security Architecture Demo\n")

# ════════════════════════════════════════════════
# 1. KMS — تشفير البيانات الحساسة
# ════════════════════════════════════════════════
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🔑 PART 1: KMS — تشفير البيانات")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# إنشاء مفتاح تشفير
key = kms.create_key(Description='my-app-encryption-key',
                      KeyUsage='ENCRYPT_DECRYPT')
key_id = key['KeyMetadata']['KeyId']
print(f"  ✅ مفتاح التشفير: {key_id[:8]}...")

# تشفير بيانات حساسة (رقم بطاقة مثلاً)
sensitive_data = "4532-1234-5678-9012"  # رقم بطاقة ائتمان
print(f"\n  البيانات الأصلية  : {sensitive_data}")

encrypted = kms.encrypt(KeyId=key_id,
                         Plaintext=sensitive_data.encode())
encrypted_b64 = base64.b64encode(encrypted['CiphertextBlob']).decode()
print(f"  بعد التشفير (KMS) : {encrypted_b64[:40]}...")
print(f"  ← لو سرق أحد قاعدة البيانات — ما يقدر يقرأ شي! ✅")

# فك التشفير
decrypted = kms.decrypt(CiphertextBlob=encrypted['CiphertextBlob'])
print(f"\n  فك التشفير        : {decrypted['Plaintext'].decode()}")
print(f"  ← بس الخدمة اللي عندها صلاحية تقدر تفك التشفير ✅")

# ════════════════════════════════════════════════
# 2. Secrets Manager — حفظ كلمات المرور
# ════════════════════════════════════════════════
print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🗝️  PART 2: Secrets Manager — كلمات المرور")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# حفظ credentials قاعدة البيانات
db_secret = {
    "username": "admin",
    "password": "MyStr0ng!Pass#2026",
    "host":     "db.myapp.com",
    "port":     5432,
    "dbname":   "production"
}

try:
    secrets.create_secret(
        Name='prod/myapp/database',
        Description='Production DB credentials',
        SecretString=json.dumps(db_secret)
    )
except: pass

print("  ✅ الـ credentials محفوظة في Secrets Manager")
print("\n  ❌ الطريقة الخاطئة (في الكود مباشرة):")
print('     password = "MyStr0ng!Pass#2026"  ← خطر جداً!')
print("\n  ✅ الطريقة الصحيحة (من Secrets Manager):")

# جيب الـ secret في وقت التشغيل
retrieved = secrets.get_secret_value(SecretId='prod/myapp/database')
creds = json.loads(retrieved['SecretString'])
print(f"     host    : {creds['host']}")
print(f"     user    : {creds['username']}")
print(f"     pass    : {'*' * len(creds['password'])}  ← مخفي دائماً")
print(f"  ← الكود ما يشوف الباسورد أبداً — يجيبه وقت التشغيل بس ✅")

# ════════════════════════════════════════════════
# 3. IAM — مين يوصل لإيش
# ════════════════════════════════════════════════
print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("👮 PART 3: IAM — صلاحيات Least Privilege")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# صلاحيات Lambda — بس ما يحتاجه
lambda_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ReadOnlyS3",
            "Effect": "Allow",
            "Action": ["s3:GetObject"],           # يقرأ بس — ما يحذف
            "Resource": "arn:aws:s3:::my-bucket/uploads/*"  # مجلد محدد بس
        },
        {
            "Sid": "WriteOrders",
            "Effect": "Allow",
            "Action": ["dynamodb:PutItem"],        # يكتب بس — ما يمسح
            "Resource": "arn:aws:dynamodb:*:*:table/orders"
        },
        {
            "Sid": "GetSecrets",
            "Effect": "Allow",
            "Action": ["secretsmanager:GetSecretValue"],
            "Resource": "arn:aws:secretsmanager:*:*:secret:prod/myapp/*"
        }
    ]
}

try:
    iam.create_policy(
        PolicyName='LambdaLeastPrivilege',
        PolicyDocument=json.dumps(lambda_policy)
    )
except: pass

print("  ✅ IAM Policy بـ Least Privilege:")
print("     S3      → قراءة فقط من مجلد محدد")
print("     DynamoDB→ كتابة فقط على جدول محدد")
print("     Secrets → جيب الـ secret بس")
print("     ← لو Lambda اتاخترق — المهاجم ما يقدر يحذف شي ✅")

print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎓 ملخص Security Architecture:

  KMS             = قفل على البيانات
  Secrets Manager = خزنة لكلمات المرور
  IAM Least Priv  = كل خدمة تاخذ أقل صلاحية

  هذا الـ Security Triangle اللي يسألون عنه
  في كل إنترفيو Senior SA! 🔐
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
