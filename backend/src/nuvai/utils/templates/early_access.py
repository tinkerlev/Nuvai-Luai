def generate_early_access_email(first_name: str) -> tuple[str, str]:
    subject = "✨ You're In! Welcome to Luai"

    html_body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
      <title>Welcome to Luai</title>
      <style>
        body {{
          background-color: #f9f9f9;
          font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
          color: #333333;
          padding: 0;
          margin: 0;
        }}
        .container {{
          max-width: 600px;
          margin: 40px auto;
          background: #ffffff;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 4px 24px rgba(0,0,0,0.06);
        }}
        .header {{
          background: linear-gradient(120deg, #1B1F2A, #646CFF);
          color: #ffffff;
          text-align: center;
          padding: 30px;
        }}
        .content {{
          padding: 35px 40px;
        }}
        .feature-box {{
          background-color: #eaf0ff;
          border-left: 4px solid #2E3192;
          border-radius: 8px;
          padding: 20px;
          margin: 30px 0;
        }}
        .cta {{
          display: inline-block;
          background: linear-gradient(120deg, #2E3192, #1BAEEA);
          color: white;
          text-decoration: none;
          padding: 14px 28px;
          border-radius: 30px;
          font-weight: bold;
          box-shadow: 0 4px 10px rgba(46,49,146,0.2);
        }}
        .footer {{
          background-color: #f5f7ff;
          text-align: center;
          font-size: 13px;
          color: #777777;
          border-top: 1px solid #eaeaea;
          padding: 20px;
        }}
        @media (prefers-color-scheme: dark) {{
          body {{ background-color: #1e1e1e; color: #dddddd; }}
          .container {{ background-color: #2a2a2a; }}
          .feature-box {{ background-color: #333e5a; border-left-color: #90caf9; }}
          .footer {{ background-color: #1c1c1c; color: #999999; border-top-color: #333333; }}
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
            <img src="https://luai.io/assets/luai-logo-transparent.png" src="cid:luai_logo" alt="Luai Logo" width="130" height="130" style="border-radius: 50%; background: #fff;" />
            <h1 style="margin: 20px 0 10px;">Welcome to Luai</h1>
            <p style="margin: 0;">You’re now officially on the inside! 🎉</p>
        </div>
        <div class="content">
          <p>Hello <strong>{first_name}</strong>,</p>
          <p>Thanks for signing up for early access to <strong>Luai</strong> – your AI-powered security partner.</p>
          <div class="feature-box">
            <h3>Luai will help you:</h3>
            <ul>
              <li>Spot vulnerabilities instantly with AI</li>
              <li>Meet ISO, NIST, and OWASP compliance</li>
              <li>Export reports (PDF, HTML)</li>
              <li>Scan AI- or no-code-generated files safely</li>
            </ul>
          </div>
          <p>We'll notify you the moment it's ready.</p>
          <p style="text-align:center; margin-top: 30px;">
            <a href="https://luai.io" style="display:inline-block;
                                              background:linear-gradient(120deg, #2E3192, #1BAEEA);
                                              color:#ffffff;
                                              text-decoration:none;
                                              padding:14px 28px;
                                              border-radius:30px;
                                              font-weight:bold;
                                              box-shadow:0 4px 10px rgba(46,49,146,0.2);
                                          ">
              Learn More About Luai
            </a>
          </p>
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
