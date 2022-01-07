import requests
from PIL import Image
import hashlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# requests 패키지를 통해 인터넷에서 이미지 파일 가져오기
url = 'http://bit.ly/2JnsHnT'
r = requests.get(url, stream = True).raw

# pillow 패키지를 통해 이미지 출력 및 저장
img = Image.open(r)
img.show()
img.save('src.png')

# 이미지 파일 복사
BUF_SIZE = 1024
with open('src.png', 'rb') as sf, open('dst.png', 'wb') as df:
    while True:
        data = sf.read(BUF_SIZE)
        if not data:
            break
        df.write(data)

# hashlib 패키지를 통해 해시값 확인
# 해시 객체 생성
sha_src = hashlib.sha256()
sha_dst = hashlib.sha256()

# 해시 객체를 각 이미지에 대한 해시값으로 업데이트
with open('src.png', 'rb') as sf, open('dst.png', 'rb') as df:
    sha_src.update(sf.read())
    sha_dst.update(df.read())

print("src.png's hash : {}".format(sha_src.hexdigest()))
print("dst.png's hash : {}".format(sha_dst.hexdigest()))

# matplotlib 패키지를 통해 이미지 가공 및 출력
plt.suptitle('Image Processing', fontsize = 18)

plt.subplot(1, 2, 1) # 1행 2열의 1번째
plt.title('Original Image')
plt.imshow(mpimg.imread('src.png'))

plt.subplot(122)
plt.title('Pseudocolor Image')
# 의사 색상 적용
dst_img = mpimg.imread('dst.png')
pseudo_img = dst_img[:, :, 0]
plt.imshow(pseudo_img)

plt.show()