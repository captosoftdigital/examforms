# 🚀 Deploy ExamForms.org NOW - Simple 3-Step Process

## Step 1: Connect to Your Server

Open your terminal (PowerShell on Windows, Terminal on Mac/Linux) and run:

```bash
ssh root@72.62.213.183
```

When prompted, enter password: `RootUser@2025`

---

## Step 2: Download and Run Deployment Script

Once connected to your server, copy and paste these commands:

```bash
# Download the deployment script
curl -o deploy.sh https://raw.githubusercontent.com/captosoftdigital/examforms/main/deploy.sh

# Make it executable
chmod +x deploy.sh

# Run the deployment
./deploy.sh
```

**OR** if the above doesn't work, manually create the script:

```bash
# Create the script file
nano deploy.sh
```

Then copy the ENTIRE content from `deploy.sh` file in your project and paste it into the nano editor.

Save with: `Ctrl+X`, then `Y`, then `Enter`

Then run:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## Step 3: Configure DNS (While Script Runs)

While the deployment script is running (takes 5-10 minutes), configure your DNS:

### Go to Hostinger Control Panel → DNS Settings

Add these records:

**Record 1:**
- Type: `A`
- Name: `@`
- Points to: `72.62.213.183`
- TTL: `3600`

**Record 2:**
- Type: `A`
- Name: `www`
- Points to: `72.62.213.183`
- TTL: `3600`

Click **Save**

---

## ✅ After Deployment Completes

The script will show you:

```
✅ DEPLOYMENT COMPLETED SUCCESSFULLY!

🌐 Your website is now accessible at:
   - http://72.62.213.183
   - http://examforms.org (after DNS propagates)

🔐 Admin Panel:
   - URL: http://72.62.213.183/admin/
   - Username: admin
   - Password: Admin@2026!Secure
```

---

## 🔒 Install SSL Certificate (After DNS Works)

Wait 5-30 minutes for DNS to propagate, then run:

```bash
certbot --nginx -d examforms.org -d www.examforms.org
```

Follow the prompts:
- Enter your email
- Agree to terms (Y)
- Redirect HTTP to HTTPS (2)

---

## 🎉 Done!

Your website will be live at:
- ✅ https://examforms.org
- ✅ https://www.examforms.org
- ✅ https://examforms.org/admin/

---

## 🚨 If Something Goes Wrong

Check the logs:
```bash
# Gunicorn logs
journalctl -u gunicorn -n 50

# Nginx logs
tail -f /var/log/nginx/error.log

# Restart services
systemctl restart gunicorn nginx
```

---

## 📞 Need Help?

If you see any errors:
1. Copy the error message
2. Share it with me
3. I'll help you fix it immediately!

---

**🚀 Let's Get Your Multi-Billion Dollar Platform LIVE! 💎**
