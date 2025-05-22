def generate_followup_email(first_name: str) -> tuple[str, str]:
    subject = "👀 A quick update from Luai..."

    html_body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
      <title>Luai Update</title>
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
        .highlight {{
          background-color: #eaf0ff;
          padding: 20px;
          border-radius: 8px;
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
          .highlight {{ background-color: #333e5a; }}
          .footer {{ background-color: #1c1c1c; color: #999999; }}
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
            <img src="https://luai.io/assets/luai-logo-transparent.png" src="cid:luai_logo" alt="Luai Logo" width="130" height="130" style="border-radius: 50%; background: #fff;" />
          <h1 style="margin:0;">Luai is Almost Ready</h1>
        </div>
        <div class="content">
          <p>Hey <strong>{first_name}</strong>,</p>

          <p>Thanks again for signing up for early access 🙌</p>

          <div class="highlight">
            <p><strong>Just a sneak peek of what’s coming:</strong></p>
            <ul>
              <li>⚡ Lightning-fast code scanning</li>
              <li>🛡️ Smart detection of vulnerabilities, even in AI-generated code</li>
              <li>📄 Exportable reports (PDF, HTML)</li>
              <li>✅ ISO/NIST/OWASP-ready recommendations</li>
            </ul>
          </div>

          <p>We're putting the final touches on Luai. You’ll get an invite as soon as it’s live. In the meantime, feel free to reply to this email and tell us what security challenges you face – we’re listening.</p>

          <p style="text-align:center; margin-top: 30px;">
            <a href="https://luai.io" style="display:inline-block;
                                              background:linear-gradient(120deg, #2E3192, #1BAEEA);
                                              color:#ffffff;
                                              text-decoration:none;
                                              padding:14px 28px;
                                              border-radius:30px;
                                              font-weight:bold;
                                              box-shadow:0 4px 10px rgba(46,49,146,0.2);
                                              text-align:center;"> See What's Coming</a>
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
