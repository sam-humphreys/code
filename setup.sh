#!/bin/bash
cd ~/code

# Install, create & activate a virtual environment
pip3 install virtualenv
virtualenv venv
source venv/bin/activate

# Install repo requirements
python setup.py install
pip install -r requirements.txt

echo "Do you want to permanatly add code as PYTHONPATH to your virtual environment activate script?"
echo "(This would save exporting PYTHONPATH upon each virtual environment activation)"
read -p "Enter 'Y' for yes, or any other key for one off in this terminal: " answer

if [ "${answer}" == 'Y' ]
then
    echo "Adding PYTHONPATH permanently to virtual environment activate script"
    echo 'export PYTHONPATH=":/code"' >> venv/bin/activate
fi

# Add to current terminal session regardless of answer (in order to run commands)
export PYTHONPATH=":/code"

echo "Setup complete!"
echo "To run commands native to this repo, enter 'coderun' - see the README for more details"