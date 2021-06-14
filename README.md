# LUS final project
**Rasa based dialog system within the book domain**.  
Final project for *Language Understanding Systems* course @ UNITN

The detailed description of the whole dialog system can be found inside the `report.pdf`. 

### ⚙️ Requirements

- `Python 3.6.*`, `3.7.*` or `3.8.*` (for this project `Python 3.7.10` has been used)
- [`Rasa`](https://rasa.com/docs/rasa/installation)
- [`Rasa X`](https://rasa.com/docs/rasa-x/)

### 🔧 How to use

- Clone the repository [`https://github.com/sebastianochiari/LUS-final-project`](https://github.com/sebastianochiari/LUS-final-project)
- Install all the dependencies listed above

### 🔊 Actions

The following list contains all the possible questions the bot is able to intend and respond:
- search the F1 championship winner given the year 
> `who won the 2020 F1 Grand Prix?`
- search a driver given its name
> `what can you tell me about Carlos Sainz?`
- search the drivers by the constructor name and the year (*optional*, if nothing is specified it tries to look within the current year) (working with forms, maybe not necessary)  
> `2014 Ferrari drivers`