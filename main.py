from pytube import Playlist
import os

# Link = "https://www.youtube.com/watch?v=Vde5SH8e1OQ&list=PLzMcBGfZo4-lB8MZfHPLTEHO9zJDDLpYj"
#
# yt_playlist = Playlist(Link)
#
# for video in yt_playlist.videos:
#     file_list = os.listdir("F:\Downloads\PyQt5_Tutorial")
#     if video.title in file_list:
#         print(f"Video Download {video.title}")
#     else:
#         vd = video.streams.get_highest_resolution()
#         vd.download("F:\Downloads\PyQt5_Tutorial")
#         print(f"Video Download {video.title}")
#
# print("All videos downloaded")


import os
import sys


def inputlist(data, k, n):
    S = 0
    #data = [int(i) for i in data]
    #data.sort()
    print(data)

    for i in range(n):
        for j in range(i, n):
            if k!=0:
                if (int(data[i]) + int(data[j])) % k == 0:
                    print(i, j)
                    S = S + 1
    return S


if __name__ == "__main__":

    lst1 = input().split()
    data = input().split()

    print(lst1)
    # print(data)
    # print(filter(lst1, "\n"))
    # data = lst1[2:]
    # print(data)
    #
    n = len(data)
    k = int(lst1[1])
    #
    print(n, k)
    print(inputlist(data, k, n))


#100 1 1000000000 1000000000 1000000000 -382075857 19871564 13895106 406276610 -51206147 -401456837 325043500 -800000000 -800000000 -800000000 163584015 -103871736 -363888144 80266180 -198548280 50308435 298393683 800000000 800000000 800000000 -253050401 -208117844 387706180 62402491 -382718491 76862941 -163877119 -800000000 -800000000 -800000000 -40408159 -160414687 -312220899 527820563 -549423370 348144080 287405318 800000000 800000000 800000000 34789030 -595028712 447250587 279711618 -78853169 -154050789 60673750 -800000000 -800000000 -800000000 358474007 -2248916 -554006720 -91844535 -102174296 264175406 -259750797 800000000 800000000 800000000 59583722 48267410 -432725222 -70783813 -18881098 404949614 -52954337 -800000000 -800000000 -800000000 18167973 366450462 -556658021 598174202 -523973700 -126646535 593696747 800000000 800000000 800000000 46658839 -133893847 215423637 -248679283 69177007 361617254 15852031 -800000000 -800000000 -800000000 232026814 -222103289 152857890 -257317304 156876057 38377618 -21455204