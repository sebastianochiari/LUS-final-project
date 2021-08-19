# LUS final project
**Rasa based dialog system within the book domain**.  
Final project for *Language Understanding Systems* course @ UNITN

The detailed description of the whole dialog system can be found inside the `report.pdf`. 

## ⚙️ Requirements

- `Python 3.6.*`, `3.7.*` or `3.8.*` (for this project `Python 3.7.10` has been used)
- [`Rasa`](https://rasa.com/docs/rasa/installation)
- [`Rasa X`](https://rasa.com/docs/rasa-x/)

## 🔧 How to use

- Clone the repository [`https://github.com/sebastianochiari/LUS-final-project`](https://github.com/sebastianochiari/LUS-final-project)
- Install all the dependencies listed above  
```
pip3 install -U pip 
pip3 install rasa 
pip3 install rasa-x --extra-index-url https://pypi.rasa.com/simple
```
- Train the model  
```
rasa train
```
> This will store a zipped model file in the `models/` folder and set the latest trained model as active.
- To chat with the bot on your local machine, you need to start two servers on two different terminals
```
rasa shell
rasa run actions
```

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
