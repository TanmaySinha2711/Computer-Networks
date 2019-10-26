#!/usr/bin/env python
import socket
import re
import sys

def get_html_page(url, s, sid, token):                                     # This function gets the HTML content of the page directed by the link
    get_str = "GET " +url +" HTTP/1.1\nHost: cs5700f18.ccs.neu.edu\nConnection: keep-alive\nCookie: " \
                         "csrftoken="+ token[0] +"; sessionid="+ sid[0] +"\r\n\r\n"
    s.send(get_str.encode())
    return s.recv(4096).decode()                                           # returns the HTML content


def get_links(page, to_crawl, visited):                                    # This fuction gets all the links from the given page by searching their href tags
    links = re.findall('<a href="(.*?)"', page)                            # used regex to find all links in the page
    for l in links:
        if l not in visited:
            if l not in to_crawl:
                to_crawl.append(l)                                         # append the link to the to_crawl list
    return to_crawl                                                        # returns the to_crawl list

def crawl(url, s, sid, token, num_flags, to_crawl, visited):               # crawl function parses all the page
    to_crawl.append(url)                                                   # starts by crawling the page /fakebook/                                                    $

    try:
        while num_flags <= 5:
            link = to_crawl.pop(0)

            if link not in visited:                                         #only crawl if link is not visited
                page = get_html_page(link, s, sid, token)

                if page.find('HTTP/1.1 30') != -1:                          #handle 302 301 pages. Direct to the link in Location tag
                    data = re.findall(r'Location:\s.*//.*?(/.*)', page, re.I)[0]
                    new_get_req = "GET " + data\
                              + " HTTP/1.1\nHost: cs5700f18.ccs.neu.edu\nConnection: keep-alive\nCookie: csrftoken="\
                              + token[0] + "; sessionid=" + sid[0] + "\r\n\r\n"
                    s.send(new_get_req.encode())
                    new_html = s.recv(10000).decode()
                    to_crawl = get_links(new_html, to_crawl, visited)
                    visited.append(link)
                elif page.find('HTTP/1.1 40') != -1:                        #handle 403 and 404 pages
                    visited.append(link)
                elif page.find('HTTP/1.1 500 INTERNAL SERVER ERROR') != -1: #handle 500 internal error
                    s.close()
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect(("cs5700f18.ccs.neu.edu", 80))
                    get_link = "GET " + link + \
                               " HTTP/1.1\nHost: cs5700f18.ccs.neu.edu\nConnection: keep-alive\nCookie: csrftoken=" \
                               + token[0] + "; sessionid=" + \
                               sid[0] + "\r\n\r\n"
                    s.send(get_link.encode())
                    new_html = s.recv(10000).decode()
                    to_crawl = get_links(new_html, to_crawl, visited)
                    visited.append(link)
                else:                                                       #handle 200 code pages. Search for flags in them
                    to_crawl = get_links(page, to_crawl, visited)
                    visited.append(link)

                    s.close()
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect(("cs5700f18.ccs.neu.edu", 80))
                    try:
                        flags = re.findall('<h2.*?>FLAG: (.*?)<', page)[0]  #use regex to find flags
                        num_flags = num_flags + 1
                        print(flags)
                        if num_flags==5:
                            sys.exit()
                    except IndexError as e:
                        pass

    except socket.timeout as e:                                               #in case of timeout re-establish the connection
        start(num_flags, to_crawl, visited)
    except TimeoutError as e:
        start(num_flags, to_crawl, visited)

def start(num_flags, to_crawl, visited):

    username = sys.argv[1]                 
    password = sys.argv[2]                                                                                            # fetching password from command line

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                                             #creating a socket
    s.connect(('cs5700f18.ccs.neu.edu', 80))                                                                          #connecting to server
    s.send("GET /accounts/login/ HTTP/1.1\nHost: cs5700f18.ccs.neu.edu\nConnection: keep-alive\r\n\r\n".encode())     #Sending GET request
    a = s.recv(100000).decode()

    token = re.findall(r'csrftoken=(\w+)', a)                                                                         #find csrftoken and stored in a variable token
    sid = re.findall(r'sessionid=(\w+)', a)                                                                           #find sessionid and stored in a variable sid

    p1 = "POST /accounts/login/ HTTP/1.1\r\nHost: cs5700f18.ccs.neu.edu\r\n"
    p2 = "Cookie: csrftoken="+token[0]+"; sessionid="+sid[0]+"\r\nContent-Length: 109\r\n\r\n"
    p3 = "username="+username+"&password="+password+"&csrfmiddlewaretoken="+token[0]+"&next=%2Ffakebook%2F"
    post_msg = p1 + p2 + p3
    s.send(post_msg.encode())                                                                                         #Send a POST request
    b = s.recv(100000).decode()

    if re.search("Please enter a correct username and password", b) or \
            re.search("500 Internal Server Error", b):
        print("Invalid username password")
        s.close()
    new_sid = re.findall(r'sessionid=(\w+)', b)                                                                       #find new sessionid after logging in

    try:
        crawl("/fakebook/", s, new_sid, token,num_flags, to_crawl, visited)
    except IndexError:
        pass


to_crawl = []
visited = ['http://www.northeastern.edu', 'mailto:aanjhan@northeastern.edu']
num_flags = 0

start(num_flags, to_crawl, visited)