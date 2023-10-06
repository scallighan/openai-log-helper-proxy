import os
import time
import logging
import tiktoken
import re
import json


logging.basicConfig(filename="/var/log/loghelper_openai.log",
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG)

logger = logging.getLogger(__name__)

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

headers_regex = re.compile(r"(\S+): (\S+)")

def parse_headers(headers: str) -> dict:
    """Parses a string of HTTP headers into a dictionary."""
    headers_dict = {}
    matches = headers_regex.findall(headers)
    for m in matches:
            headers_dict[m[0]] = m[1]
    return headers_dict

parse_resp_body_regex = re.compile(r"data: (.+)")

def parse_resp_body(resp_body: str) -> dict:
    """Parses a string of HTTP response body into a dictionary."""
    resp_body_dict = {
        "data": []
    }
    matches = parse_resp_body_regex.findall(resp_body.encode("utf-8").decode('unicode-escape'))
    #logger.info(matches)
    for m in matches:
        try:
            j = json.loads(m.replace(':nul l,', ':null,').replace(':nu ll,', ':null,').replace(':n ull,', ':null,'))
            clean_j = cleanup_json(j)
            resp_body_dict["data"].append(clean_j)
        except Exception as e:
            logger.info(f"NOT JSON: {m}")

    return resp_body_dict

def cleanup_json(d: dict) -> dict:
    clean_dict = {}
    for k, v in d.items():
        new_key = k.replace(" ", "")
        if isinstance(v, dict):
            new_v = cleanup_json(v)
            clean_dict[new_key] = new_v
        elif isinstance(v, list):
            new_v = []
            for i in v:
                if isinstance(i, dict):
                    new_v.append(cleanup_json(i))
                else:
                    new_v.append(i)
            clean_dict[new_key] = new_v
        elif isinstance(v, str) or isinstance(v, bytes):
            clean_dict[new_key] = f"{v}"
        else: 
            clean_dict[new_key] = v
    return clean_dict

def main_tail():
    logger.info("lets start the tail process...")
    for line in tail('/var/log/nginx_access.log'):
            line_split = line[0].split('" ||| "')
            logger.info("---")
            logger.info(parse_headers(line_split[2]))
            logger.info("-")
            resp_body = parse_resp_body(line_split[3])
            resp_body_arr = []
            logger.info(len(resp_body["data"]))
            for d in resp_body["data"]:
                try:
                    if "choices" in d and len(d["choices"]) > 0 and "delta" in d["choices"][0] and "content" in d["choices"][0]["delta"]:
                        resp_body_arr.append(d["choices"][0]["delta"]["content"])
                except Exception as e:
                    logger.info(f"Cannot logger.info content: {d}")
                    logger.info(f"Because of: {e}")
            logger.info("".join(resp_body_arr))
            logger.info("-------------------------")
       
# https://medium.com/@aliasav/how-follow-a-file-in-python-tail-f-in-python-bca026a901cf
def follow(f):
    '''generator function that yields new lines in a file
    '''
    # seek the end of the file
    f.seek(0, os.SEEK_END)
    # start infinite loop
    while True:
        # read last line of file
        line = f.readline()
        # sleep if file hasn't been updated
        if not line:
            time.sleep(0.1)
            continue

        yield line   


def main():
    logfile = open("/var/log/nginx_access.log","r")
    loglines = follow(logfile)
    # iterate over the generator
    for line in loglines:
        try:
            line_split = line.split('" ||| "')
            logger.info("---")
            # resp headers
            logger.info(parse_headers(line_split[2]))
            logger.info("-")
            resp_body = parse_resp_body(line_split[3])
            resp_body_arr = []
            logger.info(len(resp_body["data"]))
            for d in resp_body["data"]:
                try:
                    if "choices" in d and len(d["choices"]) > 0 and "delta" in d["choices"][0] and "content" in d["choices"][0]["delta"]:
                        resp_body_arr.append(d["choices"][0]["delta"]["content"])
                except Exception as e:
                    logger.info(f"Cannot logger.info content: {d}")
                    logger.info(f"Because of: {e}")
            resp_body_content = "".join(resp_body_arr)
            logger.info(resp_body_content)
            logger.info(f"Number of Tokens: {num_tokens_from_string(resp_body_content, 'cl100k_base')}")
            logger.info("-------------------------")
        except Exception as e:
            logging.error(f"Error in tailing: {e}")

if __name__ == "__main__":
    logger.info("start main...")
    #asyncio.run(main())
    main()
    logger.info("stop main...")