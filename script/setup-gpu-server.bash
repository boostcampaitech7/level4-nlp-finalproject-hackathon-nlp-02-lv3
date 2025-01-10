#!/bin/bash

##########################################
# GPU 서버 인스턴스 생성 시 필요한 개발 환경 세팅
# conda 미설치 환경에서는 conda 설치 과정을 추가
# 유저명 / 디렉토리 / 권한 설정 등 수정하여 사용
##########################################

##################### Install #####################
apt-get update
apt-get install -y sudo
sudo apt-get install -y wget git vim build-essential

##################### Set root password #####################
echo "root:root" | chpasswd

##################### conda #####################
export PATH="/opt/conda/bin:$PATH"
conda init bash
conda config --set auto_activate_base false
source ~/.bashrc
conda create -n main python=3.10.13 -y
sudo chmod -R 777 /opt/conda/env

##################### Users: dir & permission #####################
users=("camper")

for i in "${!users[@]}"; do
    user="${users[$i]}"
    user_folder="/data/ephemeral/home/$user"

    # Create user with custom home directory and give sudo privileges
    sudo mkdir -p $user_folder
    sudo chmod 777 $user_folder
    sudo adduser --disabled-password --home $user_folder --gecos "" $user
    # Set user password same as username
    echo "${user}:${user}" | sudo chpasswd
    sudo chsh -s /bin/bash $user
    echo "$user ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/$user

done

##################### Users: conda #####################
for user in "${users[@]}"; do
    user_folder="/data/ephemeral/home/$user"

    # Add conda to each user's PATH and initialize conda
    su - $user bash -c 'export PATH="/opt/conda/bin:$PATH"; conda init bash; conda config --set auto_activate_base false; source ~/.bashrc;'
    echo "cd $user_folder" | sudo tee -a $user_folder/.bashrc
    echo 'conda activate main' | sudo tee -a $user_folder/.bashrc

    # Add local bin path to each user's .bashrc
    echo "export PATH=\$PATH:/data/ephemeral/home/$user/.local/bin" | sudo tee -a $user_folder/.bashrc

    sudo chmod -R 777 $user_folder
    sudo chown -R $user:$user $user_folder

done

##################### Git #####################
users=("sujin" "seongmin" "sungjae" "gayeon" "yeseo" "minseo")
BASE_DIR="/data/ephemeral/home/camper"

# 각 사용자별 디렉토리 생성
for user in "${users[@]}"; do
    mkdir -p "$BASE_DIR/$user"
done

# 글로벌 .gitconfig 생성
cat << EOF > "$BASE_DIR/.gitconfig"
[user]
    name = Camper User
    email = camper@example.com

# 사용자별 폴더 설정 포함
EOF

# includeIf 설정을 동적으로 추가
for user in "${users[@]}"; do
    cat << EOF >> "$BASE_DIR/.gitconfig"
[includeIf "gitdir:$BASE_DIR/$user/"]
    path = $BASE_DIR/$user/.gitconfig
EOF
done

# 각 사용자 폴더에 .gitconfig 생성
for user in "${users[@]}"; do
    cat << EOF > "$BASE_DIR/$user/.gitconfig"
[user]
    name = $user
    email = $user@example.com
EOF
done

# 권한 설정
chown -R camper:camper "$BASE_DIR"
chmod -R 755 "$BASE_DIR"

echo "Git configuration setup completed!"

echo "Setup complete!"



##### git은 각자 폴더에서 세팅 #####
# git clone https://"$token"@github.com/boostcampaitech7/level4-nlp-finalproject-hackathon-nlp-02-lv3

# git config --local user.email "$email"
# git config --local user.name "$username"
# git config --local credential.helper "cache --timeout=360000"
# git config --local commit.template .gitmessage.txt
