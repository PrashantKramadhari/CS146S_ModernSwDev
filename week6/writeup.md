# Week 6 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 





## Brief findings overview 
> TODO

## Fix #1
a. File and line(s)
> TODO

b. Rule/category Semgrep flagged
> TODO

c. Brief risk description
> TODO

d. Your change (short code diff or explanation, AI coding tool usage)
> TODO

e. Why this mitigates the issue
> TODO

## Fix #2
a. File and line(s)
> TODO

b. Rule/category Semgrep flagged
> TODO

c. Brief risk description
> TODO

d. Your change (short code diff or explanation, AI coding tool usage)
> TODO

e. Why this mitigates the issue
> TODO

## Fix #3
a. File and line(s)
> TODO

b. Rule/category Semgrep flagged
> TODO

c. Brief risk description
> TODO

d. Your change (short code diff or explanation, AI coding tool usage)
> TODO

e. Why this mitigates the issue
> TODO

## My finding :: Backend
## 1st iter
 backend/app/main.py
    ❯❱ python.fastapi.security.wildcard-cors.wildcard-cors
          CORS policy allows any origin (using wildcard '*'). This is insecure and should be avoided.
          Details: https://sg.run/KxApY                                                              
                                                                                                     
           24┆ allow_origins=["*"],
                                               
    backend/app/routers/notes.py
   ❯❯❱ python.sqlalchemy.security.audit.avoid-sqlalchemy-text.avoid-sqlalchemy-text
          sqlalchemy.text passes the constructed SQL statement to the database mostly unchanged. This means  
          that the usual SQL injection protections are not applied and this function is vulnerable to SQL    
          injection if user input can reach here. Use normal SQLAlchemy operators (such as `or_()`, `and_()`,
          etc.) to construct SQL.                                                                            
          Details: https://sg.run/yP1O                                                                       
                                                                                                             
           71┆ sql = text(
           72┆     f"""
           73┆     SELECT id, title, content, created_at, updated_at
           74┆     FROM notes
           75┆     WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
           76┆     ORDER BY created_at DESC
           77┆     LIMIT 50
           78┆     """
           79┆ )
   
    ❯❱ python.lang.security.audit.eval-detected.eval-detected
          Detected the use of eval(). eval() can be dangerous if used to evaluate dynamic content. If this 
          content can be input from outside the program, this may be a code injection vulnerability. Ensure
          evaluated content is not definable by external sources.                                          
          Details: https://sg.run/ZvrD                                                                     
                                                                                                           
          104┆ result = str(eval(expr))  # noqa: S307
   
   ❯❯❱ python.lang.security.audit.subprocess-shell-true.subprocess-shell-true
          Found 'subprocess' function 'run' with 'shell=True'. This is dangerous because this call will spawn
          the command using a shell process. Doing so propagates current shell settings and variables, which 
          makes it much easier for a malicious actor to execute commands. Use 'shell=False' instead.         
          Details: https://sg.run/J92w                                                                       
                                                                                                             
           ▶▶┆ Autofix ▶ False
          112┆ completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)  # noqa:
               S602,S603                                                                           
   
    ❯❱ python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected
          Detected a dynamic value being used with urllib. urllib supports 'file://' schemes, so a dynamic    
          value controlled by a malicious actor may allow them to read arbitrary files. Audit uses of urllib  
          calls to ensure user data cannot control the URLs, or consider using the 'requests' library instead.
          Details: https://sg.run/dKZZ                                                                        
                                                                                                              
          120┆ with urlopen(url) as res:  # noqa: S310

                
                
┌──────────────┐
│ Scan Summary │
└──────────────┘
✅ Scan completed successfully.
 • Findings: 5 (5 blocking)
 • Rules run: 291
 • Targets scanned: 10
 • Parsed lines: ~100.0%
 • Scan skipped: 
   ◦ Files matching .semgrepignore patterns: 5
 • For a detailed list of skipped files and lines, run semgrep with the --verbose flag
Ran 291 rules on 10 files: 5 findings.
💎 Missed out on 1390 pro rules since you aren't logged in!
⚡ Supercharge Semgrep OSS when you create a free account at https://sg.run/rules.

## 2nd iter
## My finding :: Frontend

  frontend/app.js
   ❯❯❱ javascript.browser.security.insecure-document-method.insecure-document-method
          User controlled data in methods like `innerHTML`, `outerHTML` or `document.write` is an anti-pattern
          that can lead to XSS vulnerabilities                                                                
          Details: https://sg.run/LwA9                                                                        
                                                                                                              
           14┆ li.innerHTML = `<strong>${n.title}</strong>: ${n.content}`;

                
                
┌──────────────┐
│ Scan Summary │
└──────────────┘
✅ Scan completed successfully.
 • Findings: 1 (1 blocking)
 • Rules run: 218
 • Targets scanned: 3
 • Parsed lines: ~100.0%
 • No ignore information available
Ran 218 rules on 3 files: 1 finding.
💎 Missed out on 1390 pro rules since you aren't logged in!
⚡ Supercharge Semgrep OSS when you create a free account at https://sg.run/rules
