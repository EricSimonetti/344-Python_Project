import glob
import os
import re
import zipfile
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders


def get_file_info(dir):
    directories = [f for f in glob.glob(dir+"*")]


    files = []
    for ext in ('*/*.pro', '*/*.py', '*/src/*.scala', '*/src/*/*.clj', '*/*.c'):
        files.extend(glob.glob(dir + ext))

    file_names = []
    for i in range(len(files)):
        file_names.append(os.path.basename(files[i]))

    relfiles = []
    for r in range(len(file_names)):
        if r == 2:
            relfiles.append("src/" + file_names[r])
        elif r == 3:
            relfiles.append("src/clojure_assignment/" + file_names[r])
        else:
            relfiles.append(file_names[r])

    num_lines = []
    for f in files:
        num_lines.append(os.popen("wc -l " + f).read().split(' ', 1)[0])

    return directories, files, file_names, num_lines, relfiles


def get_HTML_files(directories, files, file_names, num_lines, relfiles):
    all_identifiers = get_identifiers(files)
    identifiers = []
    for ids in range(len(all_identifiers)):
        identifiers.append("")
        for id in range(len(all_identifiers[ids])):
            if id % 10 == 0:
                identifiers[ids] = identifiers[ids] + "\n"
            identifiers[ids] = identifiers[ids] + " " + all_identifiers[ids][id]

    html_files = []
    html_temp = []
    for i in range(len(directories)):
        html_temp.append(directories[i] + "/summary_" + os.path.basename(directories[i]) + ".html")
        f = open(html_temp[i], "w+")
        f.write("<html>\n"
                "<head>" +
                "<name>" +
                "File name: " + "<a href = " + relfiles[i] + ">" + file_names[i] + "</a>" +
                "</name>" +
                "<lines>" +
                " Number of lines: " + num_lines[i] +
                "</lines>" +
                "</head>\n"
                "<body>" +
                "<identifiers>" +
                "Identifiers: " + identifiers[i] +
                "</identifiers>" +
                "</body>\n"
                "</html>")
        f.close()

    for h in range(len(html_temp)):
        index = html_temp[h].index("344/")
        rel = (html_temp[h])[index+4:len(html_temp[h])]
        html_files.append(rel)

    return html_temp, html_files


def get_identifiers(files):
    all_identifiers = []
    for i in range(len(files)):
        with open(files[i], "r") as file:
            identifiers = set(())
            words = []
            for line in file:
                if not line.startswith('#') and \
                   not line.startswith('//') and \
                   not line.startswith('%'):
                    words.extend(line.split())

            for word in range(len(words)):
                if re.match("[a-zA-Z0-9_]+", words[word]):
                    identifiers.add(re.match("[a-zA-Z0-9_]+", words[word]).group(0))
            all_identifiers.append(list(identifiers))

    return all_identifiers


def make_webpage(dir, html_files, file_names):
    links = ""
    for i in range(len(html_files)-1):
        links = links + "<a href = " + html_files[i] + ">" + file_names[i] + "</a> |\n"
    links = links + "<a href = " + html_files[len(html_files)-1] + ">" + file_names[len(html_files)-1] + "</a>\n"
    head = """<html>

                <head>
                    <title>Project WebPage</title>
                </head>
                
                <body>
                    <div id = "menu" align = "middle" >\n"""
    tail = """      </div>
                </body>
                
            </html>"""
    webpage = open(dir+"webpage.html", "w+")
    webpage.write(head+links+tail)
    return dir+"webpage.html"


def get_zip(directory, html_files, files, webpage):
    zip_directory = directory + 'esimonet344.zip'
    zip = zipfile.ZipFile(directory + 'esimonet344.zip', 'w', zipfile.ZIP_DEFLATED)
    for html_file in html_files:
        zip.write(html_file)
    for file in files:
        zip.write(file)
    zip.write(webpage)
    return zip_directory


def send_email(email, my_zip):
    FROM = "esimonet@oswego.edu"
    subject = "Python project email"
    text = "Hey Dan, \n\n" \
           "Hopefully you got this email! The zip file should be attached.\n\n" \
           "Have a great summer!\n" \
           "Eric"

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = FROM
    msg['To'] = email
    msg.attach(MIMEText(text))
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(my_zip, 'rb').read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename=' + my_zip)
    msg.attach(part)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(user=FROM, password='CompSci22')
    s.sendmail(FROM, email, msg.as_string())
    s.quit()


def main():
    directory = "/home/csc241/Desktop/Assignments/second_semester/programming_languages/344/"
    directories, files, file_names, num_lines, relfiles = get_file_info(directory)
    html_files, html_rel = get_HTML_files(directories, files, file_names, num_lines, relfiles)
    webpage = make_webpage(directory, html_rel, file_names)
    my_zip = get_zip(directory, html_files, files, webpage)
    email = input("Enter your email.")
    send_email(email, my_zip)
    print("Email sent to " + email)


main()