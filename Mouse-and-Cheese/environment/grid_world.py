from pathlib import Path

import pygame
from PIL import Image


def load_png(path):
    """Pillow経由でPNG画像を読み込む（SDL_imageが無い環境用）"""
    pil_img = Image.open(path).convert("RGBA")
    return pygame.image.frombuffer(pil_img.tobytes(), pil_img.size, "RGBA")

#ゲームの環境
class grid_world:
    def __init__(self): #インスタンスを初期化
        pass
        # pygameを初期化
        pygame.init()

        # grid_sizeを設定
        self.grid_size = 32

        # xlenとylenを設定
        self.xlen = 15
        self.ylen = 15

        # xlenとylenから画面の縦横の大きさを設定
        width = self.grid_size*self.xlen
        height = self.grid_size*self.ylen
        window_size = (width, height)

        # 表示する画面を作成
        self.screen = pygame.display.set_mode(window_size)

        # 画像のパスの読み込み
        #ネズミ=agent
        agent_img_path = Path('images/agent.png')
        self.img_agent = load_png(agent_img_path)
        #チーズ=reward
        reward_img_path = Path('images/cheese.png')
        self.img_reward = load_png(reward_img_path)

        # チーズとネズミの画像をgrid_sizeの大きさに合わせて読み込む
        self.img_agent = pygame.transform.smoothscale(self.img_agent, (self.grid_size, self.grid_size))
        self.img_reward = pygame.transform.smoothscale(self.img_reward, (self.grid_size, self.grid_size))

        # 背景の画像を読みこむ
        chip_img_path = Path('images/chip.png')
        self.img_bg = load_png(chip_img_path)

        # ネズミとチーズの初期位置を設定
        self.agent_pos = [1, 1]
        self.reward_pos = [2, 12]

        # episode_counterを設定
        self.episode_counter = 10000

        # get_map_dataからmap_dataを取得
        self.map_data=self.get_map_data()

        # cycleの初期値を設定
        self.cycle = 2

    def get_map_data(self): #
        # 表示する画像の番号を格納したmap_dataを作成
        map_data = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1,
        1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1,
        1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1,
        1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1,
        1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1,
        1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1,
        1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1,
        1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1,
        1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    ]
        return map_data

        # return map_data
        

    def render(self): #
        
        # 画像の切り取りをする始点のchip_listを作成
        chip_list = [(0, 0),(32, 0),(0, 32),(32, 32)]

        # 横と縦で二重ループを作成し、背景を表示
        for y in range(0, self.ylen):
            for x in range(0, self.xlen):
                i = x + y*15
                c = self.map_data[i]
                self.screen.blit(self.img_bg,
                        (x*self.grid_size, y*self.grid_size),
                        (chip_list[c], (self.grid_size, self.grid_size)))

        # ネズミとチーズを表示
        self.screen.blit(self.img_agent, (self.agent_pos[0]*self.grid_size, self.agent_pos[1]*self.grid_size))
        self.screen.blit(self.img_reward, (self.reward_pos[0]*self.grid_size, self.reward_pos[1]*self.grid_size))

    def step(self, action):
        
        # 移動する方向を格納したaction_listを作成
        action_list = [[0, 1],[0, -1],[1, 0],[-1, 0],[0, 0]]

        # チーズの移動できる座標を格納したreward_pos_listを作成
        reward_pos_list = [[0, 0],[2, 2],[2, 12],[12, 2],[12, 12]]

        # doneをFalseに設定
        done = False

        # episode_counterを1進める
        self.episode_counter += 1

        # rewardを0.に設定
        reward = 0.

        # action_listから移動する方向を取得
        agent_action = action_list[action]

        # check関数より移動可能かを調べる
        self.agent_pos = self.check(self.agent_pos, agent_action, self.map_data)

        # チーズと同じ座標に移動したら報酬を与えて、チーズの位置を更新
        if self.agent_pos == self.reward_pos:
            self.cycle = self.cycle % 4+1
            reward += 1
            self.reward_pos = reward_pos_list[self.cycle]

        # 1000回行動した後ならdoneをTrueにする
        if self.episode_counter % 1000 == 0:
            done = True

        return self.agent_pos, reward, done
        #return (self.agent_pos, self.reward_pos, self.cycle, self.episode_counter), reward, done

    def check(self, agent_pos, action, data):
       # 移動する方向とネズミの位置を足して、移動先の座標を取得
        a_pos = [x+y for (x, y) in zip(self.agent_pos, action)]
        map_data = data[a_pos[0] + a_pos[1]*15]

        # もし移動先のマスに表示されている画像の番号が1なら移動しない
        # return self.agent_pos
        # そうでなければ移動する
        # return a_pos
        if map_data == 1:
            return self.agent_pos
        else:
            return a_pos

    def reset(self):
        
        # ネズミとチーズの位置を初期の座標に戻す
        self.agent_pos = [1, 1]
        self.reward_pos = [2, 12]

        # cycleを初期値にする
        cycle = 2

        return self.agent_pos
        # return self.agent_pos, self.reward_pos, cycle
