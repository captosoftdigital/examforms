# Fix GitHub Token Issue

## Problem
The current token doesn't have push permissions even though it shows admin access via API.

## Solution: Create a New Fine-Grained Token

### Step 1: Delete Old Token
1. Go to: https://github.com/settings/tokens
2. Find and delete the token you just created

### Step 2: Create Fine-Grained Personal Access Token
1. Go to: https://github.com/settings/personal-access-tokens/new
2. Fill in:
   - **Token name**: ExamForms Deployment
   - **Expiration**: 90 days (or your preference)
   - **Repository access**: Select "Only select repositories"
   - Choose: `captosoftdigital/examforms`
   
3. **Repository permissions** (expand and set):
   - Contents: **Read and write** ✅
   - Metadata: **Read-only** (auto-selected)
   - Pull requests: **Read and write** (optional)
   - Workflows: **Read and write** (optional)

4. Click "Generate token"
5. **Copy the new token** (starts with `github_pat_`)

### Step 3: Test the New Token

Run this command with your NEW token:

```bash
git remote remove origin
git remote add origin https://captosoftdigital:YOUR_NEW_TOKEN@github.com/captosoftdigital/examforms.git
git push -u origin main
```

## Alternative: Use Classic Token (Simpler)

If fine-grained tokens don't work:

1. Go to: https://github.com/settings/tokens/new (Classic)
2. Note: "ExamForms Push"
3. Select scopes:
   - ✅ **repo** (all sub-options)
   - ✅ **workflow**
4. Generate token
5. Use the command above with the new classic token

## Why This Happens

GitHub has two types of tokens:
- **Classic tokens**: Work with username in URL
- **Fine-grained tokens**: More secure, need specific repo permissions

The token you created might be missing the "Contents: Write" permission.
