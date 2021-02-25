# Capstone1_Restaurants (Planning Phase)

## Initial Ideas

-   Create a website that users/consumers are looking for specific restaurants or recommendations based on nearby
    locations or different cuisines (food categories), if they are open now, etc.
-   Users would be able to see/view the additional information(contract, address, menus, reviews) about the restaurants.
-   Users can 'favorite' restaurants, add food to cart to calculate total, add personal notes to a restaurants. (Users need
    to create an account to do thoses!)
-   Create a checkout system (Stripe API)

## APIs

-   Documenu https://documenu.com/docs#get_started

    -   Menu items Search (based on terms, specific restaurants, locations)

-   Yelp Fusion API https://www.yelp.com/developers/documentation/v3

    -   Restaurant Search (by keywords, location, category, open now)
    -   Restaurant Details (photos, price levels, hours of operations)

-   Geocoding API https://developers.google.com/maps/documentation/geocoding/overview

    -   Convert an address into geocoding

-   Stripe https://stripe.com/docs/api

    -   Provide checkout system that offers ways to accept card payments

## Database Schema

-   Users(id(pk), first_name(text), last_name(text), email(text,unique), password(text, hashed), created_at(timestamp), zip_code(int), birth_date(date, optional)), imageURL(text)
-   Favorites(user_id(pk, foreign_key(users.id)), business_id(fk to yelp's database))
-   Comments(id(pk), message(text), created_at(timestamp), user_id(foreign_key(users.id)), business_id(fk to yelp's database))
-   Likes(id(pk), user_id(fk(users.id)), comment_id(fk(comments.id)))
-   Carts_items(user_id(pk, fk(users.id)), item_id(pk, fk to documenu's database), quantity(int))

## User Flow

-   Landing page(home page): Search bar to a restaurant, nav bar to brand, log in, sign up button), if logged in restaurants or food items will be shown based on favorites, user’ zip code location, or recent searches, if not random food items will be shown randomly.
-   Click on the food item or the restaurant will redirect to that restaurant’s details page, where it shows all the business’ information including contract, operation hours, menu of items, price range, rating on Yelp, comments, etc.
-   Click on the Log in, user will be routed to Login page, where user can type in registered username and correct password, then redirected back to home page.
-   After typing in a search term/query, click search will route to the page where it shows search results that contain brief information.
-   To sign up click on the sign up button on the nav bar, where it redirects to a page where users can provide first name, last name, email, password, zip code, birthday(optional) to sign up an account.

## Figma wireframes

-   https://www.figma.com/file/tjitRYR6TGkKwwka3yMtae/Capstone1_Restaurants_Wireframes?node-id=0%3A1
