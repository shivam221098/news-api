import threading
import concurrent.futures
import time
import requests

img_urls = [
    'https://images.unsplash.com/photo-1516117172878-fd2c41f4a759',
    'https://images.unsplash.com/photo-1532009324734-20a7a5813719',
    'https://images.unsplash.com/photo-1524429656589-6633a470097c',
    'https://images.unsplash.com/photo-1530224264768-7ff8c1789d79',
    'https://images.unsplash.com/photo-1564135624576-c5c88640f235',
    'https://images.unsplash.com/photo-1541698444083-023c97d3f4b6',
    'https://images.unsplash.com/photo-1522364723953-452d3431c267',
    'https://images.unsplash.com/photo-1513938709626-033611b8cc03',
    'https://images.unsplash.com/photo-1507143550189-fed454f93097',

]


def do_something(t, x):
    print(f"Starting function with time {t} and {x}...")
    time.sleep(t)
    print(f"Done function with time {t} and {x}...")


def basic():
    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(do_something, i) for i in range(5, 0, -1)]

        for result in concurrent.futures.as_completed(results):
            print(result.result())


    """threads = []
    for i in range(1, 100):
        t = threading.Thread(target=do_something, args=(i,))
        t.start()
        threads.append(t)

    # print(threads)

    for thread in threads:
        thread.join()"""

    finish = time.perf_counter()

    print(f"Finished in {round(finish - start, 3)} time.")


"""def download_img(img_url):
    image = requests.get(img_url).content
    img_name = img_url.split("/")[3] + ".jpg"
    with open(img_name, "wb") as file:
        file.write(image)
    print(f"{img_name} downloaded.....")


if __name__ == "__main__":
    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(download_img, img_urls)
    finish = time.perf_counter()
    print(f"Time taken: {finish - start}")"""


if __name__ == '__main__':
    print("YO")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(do_something, 1, 2)
