
# CS50 Finance

I completed this project as part of finishing CS50, Harvard University's introduction to the intellectual enterprises of computer science and the art of programming through edX. I chose to take CS50 because I intended to spend my summer break honing my programming abilities. As this project was one of the most challenging and enjoyable projects that CS50 had to offer, I had so much fun finishing it and gained extensive knowledge about how a Flask web app functions, including sessions, user registration, linking the backend to the front end and templating with jinja engine. Since this project is more focused on the back end, I wanted to spend less time on the front end, which is different from my usual approach.

This web application allows you to manage portfolios of stocks. Not only will this tool allow you to check real stocks' actual prices and portfolios' values, but it will also let you "buy" and "sell" stocks by querying [IEX](https://exchange.iex.io/products/market-data-connectivity/) for stocks' prices. Before you start trading stocks for real money, you can use this web program to practice stock trading without risking any of your hard-earned cash.

## Run Locally

Clone the project

```bash
  git clone https://github.com/Ochirsaikhan/cs50-finance.git
```

Go to the project directory

```bash
  cd my-project
```

Install dependencies

```bash
  pip install -r requirements.txt
```

## Configuring

Before you'll be able to run this locally, you'll need to register for an API key in order to be able to query IEX’s data. To do so, follow these steps:

* Visit https://iexcloud.io/cloud-login#/register/
* Select the “Individual” account type, then enter your name, email address, and a password, and click “Create account”.
* Once registered, scroll down to “Get started for free” and click “Select Start plan” to choose the free plan.
* Once you’ve confirmed your account via a confirmation email, visit https://iexcloud.io/console/tokens.
* Copy the key that appears under the Token column (it should begin with `pk_`).
* In your terminal window, execute:

```bash
export API_KEY=value
```

Where `value` is that (pasted) value, without any space immediately before or after the `=`. You also may wish to paste that value in a text document somewhere, in case you need it again later.

## Running

Start Flask’s built-in web server while in the root directory:

```bash
flask run
```

Visit the URL outputted by Flask and register your username and password to start your journey of stock trading!

## Demo

You can visit this website https://davaajambal-cs50-finance.herokuapp.com to use the web application online.

![Project demo](/Demo.gif)

## Lessons Learned

By finishing this project, I learned a lot about the general structure of Flask projects, how Flask handles routes with GET and POST methods, and how the integration between API, database, and front end works. Additionally, I gained extensive experience handling errors, such as users trying to sell more than they own or buying more than they could afford.

As part of implementing my personal touches to this project, I created a feature in the history section that allows you to see your profit and loss by calculating the difference between the price you bought and the price you sold the stock. Also, if you made a profit, the text will appear in green; otherwise, it will appear in red. Finally, I made it possible to sell the same stock you bought at different prices with the correct profit and loss calculation.

In addition to finishing this project locally, I deployed this project to [Heroku](http://heroku.com/), a cloud platform as a service (PaaS) that lets companies build, deliver, monitor, and scale apps, to make it possible for users to use it online. I read Heroku's documentation and successfully integrated my web application with it, although there were a few hurdles. Heroku used [PostgreSQL](https://www.postgresql.org) instead of [SQLite](https://www.sqlite.org), causing some integration issues. However, I resolved the problem by reading the documentation and doing a bit of google-fu. Overall, I enjoyed working on this project a lot because it combined two of my interests—the stock market and web technologies.
