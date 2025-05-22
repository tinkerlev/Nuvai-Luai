def generate_launch_email(first_name: str, invite_link: str) -> tuple[str, str]:
    subject = "🚀 Luai is Live – Start Scanning Now!"

    html_body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
      <title>Luai Launch</title>
      <style>
        body {{
          background-color: #f9f9f9;
          font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
          color: #333;
          padding: 0;
          margin: 0;
        }}
        .container {{
          max-width: 600px;
          margin: 40px auto;
          background: #ffffff;
          border-radius: 12px;
          box-shadow: 0 4px 24px rgba(0,0,0,0.06);
          overflow: hidden;
        }}
        .header {{
          background: linear-gradient(120deg, #1B1F2A, #646CFF);
          color: white;
          text-align: center;
          padding: 40px 30px;
        }}
        .content {{
          padding: 35px 40px;
        }}
        .cta {{
          display: inline-block;
          background: linear-gradient(120deg, #2E3192, #1BAEEA);
          color: white;
          text-decoration: none;
          padding: 14px 32px;
          border-radius: 30px;
          font-weight: bold;
          box-shadow: 0 4px 10px rgba(46,49,146,0.2);
        }}
        .footer {{
          background-color: #f5f7ff;
          text-align: center;
          font-size: 13px;
          color: #777;
          border-top: 1px solid #eaeaea;
          padding: 20px;
        }}
        @media (prefers-color-scheme: dark) {{
          body {{ background-color: #1e1e1e; color: #ddd; }}
          .container {{ background-color: #2a2a2a; }}
          .footer {{ background-color: #1c1c1c; color: #999; }}
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
            <img src="https://luai.io/assets/luai-logo-transparent.png" src="cid:luai_logo" alt="Luai Logo" width="130" height="130" style="border-radius: 50%; background: #fff;" />
          <h1 style="margin:0;">Luai is Live!</h1>
          <p style="margin-top:10px; font-size:18px;">You're among the first to access it 🎉</p>
        </div>
        <div class="content">
          <p>Hi <strong>{first_name}</strong>,</p>
          <p>We're thrilled to let you know that <strong>Luai is now live</strong> and ready to help you scan your code for vulnerabilities – with the power of AI.</p>

          <p>This is your early access invite. It's unique and designed just for you:</p>

          <p style="text-align:center; margin: 30px 0;">
            <a href="{invite_link}" style="display:inline-block;
                                              background:linear-gradient(120deg, #2E3192, #1BAEEA);
                                              color:#ffffff;
                                              text-decoration:none;
                                              padding:14px 28px;
                                              border-radius:30px;
                                              font-weight:bold;
                                              box-shadow:0 4px 10px rgba(46,49,146,0.2);
                                              text-align:center;">
                                              Start Scanning Now</a>
          </p>

          <p>Luai scans your code, detects hidden flaws, and gives you clear, actionable suggestions – all in seconds.</p>

          <p style="margin-top: 30px;">Thank you for being one of the early believers</p>
        </div>
        <div class="footer">
          <p>© 2025 Luai – Your AI-Powered Security Partner</p>
          <p>
            <a href="https://luai.io/privacy" style="color:#2E3192; text-decoration:none;">Privacy</a> |
            <a href="https://luai.io/terms" style="color:#2E3192; text-decoration:none;">Terms</a> |
            <a href="https://luai.io/unsubscribe" style="color:#2E3192; text-decoration:none;">Unsubscribe</a>
          </p>
        </div>
      </div>
    </body>
    </html>
    """
    return subject, html_body
