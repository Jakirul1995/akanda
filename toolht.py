import argparse
import requests
import threading
import queue
from tqdm import tqdm

domain = []

def check_url(url, timeout=5):
    """Check the status of a URL."""
    try:
        response = requests.get(f"https://{url}", timeout=timeout, stream=True)
        if response.status_code == 200:
            domain.append(url)
    except requests.RequestException:
        pass

def worker(q, progress):
    """Thread worker function."""
    while not q.empty():
        try:
            url = q.get_nowait()
        except queue.Empty:
            return
        check_url(url)
        q.task_done()
        progress.update(1)

def main(file, threads):
    """Main function to manage threading and URL checks."""
    q = queue.Queue()

    with open(file, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        q.put(url)

    progress = tqdm(total=len(urls), desc="Checking URLs", unit="url", dynamic_ncols=True)
    thread_list = []

    for _ in range(min(threads, len(urls))):
        t = threading.Thread(target=worker, args=(q, progress), daemon=True)
        t.start()
        thread_list.append(t)

    for t in thread_list:
        t.join()

    progress.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ultra-Fast Multi-threaded URL Status Checker")
    parser.add_argument("-f", "--file", required=True, help="Path to file containing list of URLs")
    parser.add_argument("-o", "--output", required=True, help="File to save all 200 URLs", dest="out")
    parser.add_argument("-t", "--threads", type=int, default=200, help="Number of threads (default: 200)")
    args = parser.parse_args()

    main(args.file, args.threads)

    if len(domain) != 0:
        with open(args.out, "w") as outf:
            outf.writelines(f"{url}\n" for url in domain)
