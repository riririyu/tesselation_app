
import pygame

pygame.init()
# 初期の画面サイズ
size = [800, 600]
# フラグを統合
flags = pygame.RESIZABLE | pygame.DOUBLEBUF
screen = pygame.display.set_mode(size, flags)

clock = pygame.time.Clock()

while True:
    # イベントを処理
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        # リサイズイベント
        if event.type == pygame.VIDEORESIZE:
            # event.size を直接使う
            size = event.size
            # 再設定（ここがポイント：flagsを使い回す）
            screen = pygame.display.set_mode(size, flags)
            print(f"Resized to: {size}")

    screen.fill((50, 50, 100)) # 背景色
    # 画面の中央に円を描画して、サイズ変更を確認しやすくする
    pygame.draw.circle(screen, (255, 255, 255), (size[0]//2, size[1]//2), 50)
    
    pygame.display.flip()
