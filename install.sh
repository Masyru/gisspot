echo "====> making virtual env"
pip3 install virtualenv
python3 -m venv ./venv
echo "====> start virtual env"
source ./venv/bin/activate
echo "====> install from requirements.txt"
pip install -r requirements.txt
echo "====> finish install python modules"
echo
echo "====> start installing node modules"
# shellcheck disable=SC2164
cd ./frontend
npm i
npm run build
echo "====> finish install node modules"
# shellcheck disable=SC2164
cd ../backend
echo "====> start local server ====> python main.py"
python main.py