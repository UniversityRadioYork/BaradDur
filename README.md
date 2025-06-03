# BaradDur
What if the scheduler wasn't INSIDE myradio? what then huh?
We also bring in some admin tools and allow for observations at a glance for if shows actually happened.

# Setup

You can setup this up in docker, but if you want to develop it might be easier to be closer to the metal and run on your machine. Simply install the pyton env and run the the main file. Make sure to fill out the an appropriate env file.

```bash
npm i
npm run build:css
pip install -r requirements.txt
python main.py
```

The server will be live on `127.0.0.1:6339` - check, the port may be different. 

If you change the style.css file, you need to run the following command to update the tailwind CSS:

```bash
npm run build:css
```

Note this project uses Tailwind and DaisyUI for styling. If you must add global styles, you can do so in the `style.css` file in the root of the project. Do NOT edit the tailwind.css file in the `static` folder.

## Todo:
Not in priority order

- View clashes on custom time slot form update
- Include a way to update PIS News
- See a shows sign in percentages on list shows page

## Images
![image](https://github.com/user-attachments/assets/0968b776-c95b-4989-89c9-79fae7ded3c9)
![image](https://github.com/user-attachments/assets/0d0b0446-85d6-439f-805e-3a5b9f54b0db)
![image](https://github.com/user-attachments/assets/5961d129-8f91-439e-93b4-1f1f2c0dd957)
![image](https://github.com/user-attachments/assets/f2f3e66f-acb1-4656-bf46-bbaeb9ff2584)


## Credits

With thanks to the [icon image source](https://commons.wikimedia.org/wiki/Category:Eye_of_Sauron#/media/File:Flag_of_Mordor.svg) - this image was altered by removing it's backgound.
