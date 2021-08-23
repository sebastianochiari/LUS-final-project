# LUS final project
**Rasa based dialog system within the book domain**.  
Final project for *Language Understanding Systems* course @ UNITN

The detailed description of the whole dialog system can be found inside the `report` folder.

Video demonstration of the chatbot can be found [here](https://drive.google.com/file/d/1STil5DJKEMYJ8v5sCcFc9dFwbi_CzI4X/view?usp=sharing).

## ⚙️ Requirements

- `Python 3.6.*`, `3.7.*` or `3.8.*` (for this project `Python 3.7.10` has been used)
- [`Rasa`](https://rasa.com/docs/rasa/installation)
- [`Rasa X`](https://rasa.com/docs/rasa-x/) (*optional*)

## 🔧 How to use

- Clone the repository [`https://github.com/sebastianochiari/LUS-final-project`](https://github.com/sebastianochiari/LUS-final-project)
- Install all the dependencies listed above
- Train the model  
```
rasa train
```
> This will store a zipped model file in the `models/` folder and set the latest trained model as active.

### 💻 Local
To **chat with the bot on your local machine**, start two servers on two different terminals, running the following two commands
```
rasa shell
rasa run actions
```

### 🔮 Alexa
To **chat with the bot using the ASK infrastructure**, do the following instructions:

- create an Alexa Skill on [Amazon Developer](https://developer.amazon.com/it-IT/alexa/alexa-skills-kit)
- replace the JSON file in the JSON Editor with the `alexa_schema.json` you can find in the repository
- launch the following commands in three separate terminal shells
```
rasa run actions
rasa run -m models --endpoints endpoints.yml
ngrok http 5005
```
- update the endpoint on the Alexa Developer Console by selecting HTTPS, "*My development endpoint is a subdomain of a domain that has a wildcard certificate from a certificate authority*" as SSL certificate and copying the ngrok url concatenated with `webhooks/alexa_assistant/webhook`

## 🔊 Actions

The following list contains all the possible questions the bot is able to intend and respond:
- ask **what the bot is able to do**
> `what are you capable of?`
- ask for an **F1 joke** (retrived from https://upjoke.com/f1-jokes)
> `make me laugh`
- search the **F1 championship winner given the year**
> `who won the 2020 F1 championship?`
- search **driver info** given its name
> `what can you tell me about Carlos Sainz?`
- search the **drivers by constructor name and the year** (*optional*, if nothing is specified it tries to look within the current year) (working with forms, maybe not necessary)  
> `2014 Ferrari drivers`
- search a **race result** (two options, *ranking* returns the podium of the race, *driver* returns its race outcome)
> `I want to know the race results for the British Grand Prix in 2008`
- search the **next race in calendar**
> `when will be the next race?`
