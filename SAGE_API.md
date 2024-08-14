# Sage Dining API Documentation
Sage Dining has an API available for their own menu application, but, the API requires almost no authentication, so it can be used freely. I put together the following documentation based on my findings. Over time, this documentation may become inaccurate due to Sage changing their api

### Base URL: 
The Base URL for the API: `sagedining.com/rest/SageRest/v1/public/customerapp`

### Authentication
Some of the endpoints require authentication. First, you will need a valid Sage Dining account. (You can use a throwaway email service to obtain one) Then, to authenticate, use the [login](#login-post) endpoint to get a access token that for an hour. 

This token must be provided as a Bearer token for endpoints that require authentication.

### `/login` (POST)
So, technically there are multiple ways to use this endpoint, including renewing a token for active session. But, it's usually just easier to login with credentials and get a new, fresh token.

#### Parameters
* `grant` (String): Set this to `password`

```json
{
    "grant": "password"
}
```
#### Authentication
Use Basic Authentication, with an email and password for a valid SAGE account.

#### Example Response
As seen below, the credentials.accessToken is the one you will use later as the Bearer Token
```json
{
  "error": false,
  "authSuccess": true,
  "credentials": {
    "id": "105361",
    "partyId": "528481",
    "accessToken": "61v262de30acv41091894fjf938f388baceb9eff",
    "accessTokenExpiry": "2019-07-27 02:12:21",
    "refreshToken": "21fny3f71f0notreal7ffc9cfec0e5lb67xb0ef3",
    "refreshTokenExpiry": "2019-08-03 01:12:21"
  },
  "accountType": "student",
  "isManager": false,
  "id": "108617",
  "userName": "John Smith",
  "userEmail": "example@example.com",
  "emailVerified": true,
  "userUsername": "example@example.com",
  "userProfileImagePath": null,
  "allowedAccess": true,
  "allergenProfile": null,
  "associationRequests": [],
  "recommendedItems": [],
  "favorites": [],
  "school": {
    "id": "1370",
    "label": "S0140",
    "shortName": "thenewschool",
    "name": "The New School",
    "isCollege": false,
    "displayName": "School",
    "hasOnlineOrdering": false,
    "hasPerformanceSpotlight": false,
    "city": "Fayetteville",
    "state": "AR",
    "zip": "72703",
    "nameLabel": "S0140",
    "address": "2514 New School Place\\nFayetteville, AR 72703",
    "logoPath": "\/intranet\/images\/content\/logos0140.png",
    "contacts": [
      {
        "name": "Bobby Howe",
        "businessTitle": "District Manager",
        "phoneNumber": "4795217037",
        "emailAddress": "bhowe@sagedining.com",
        "employeePhotoPath": "\/intranet\/images\/employees\/bhowe.jpg"
      }
    ]
  }
}
```

### `/findschool` (GET)
Accepts a zipcode and returns schools with a corresponding zipcode. (As far as I can tell, the zipcode must match exactly)

#### Query Args
* `zip` (Number): A standard zipcode. Ex: 72703

#### Example Response
```json
{
    "error": false,
    "accessGranted": true,
    "schools": [
        {
            "id": "1370",
            "label": "S0140",
            "shortName": "thenewschool",
            "name": "The New School",
            "isCollege": false,
            "displayName": "School",
            "hasOnlineOrdering": false,
            "hasPerformanceSpotlight": false,
            "city": "Fayetteville",
            "state": "AR",
            "zip": "72703",
            "nameLabel": "S0140",
            "address": "2514 New School Place\\nFayetteville, AR 72703",
            "logoPath": "/intranet/images/content/logos0140.png",
            "contacts": [
                {
                    "name": "Bobby Howe",
                    "businessTitle": "District Manager",
                    "phoneNumber": "4795217037",
                    "emailAddress": "bhowe@sagedining.com",
                    "employeePhotoPath": "/intranet/images/employees/bhowe.jpg"
                }
            ]
        }
    ]
}
```

### `/getmenus` (GET)
Accepts a school ID and returns menus for that school

#### Query Args
* `unitId` (Number): The school's ID number. Can be found using [`/findschool`](#findschool-get)

#### Authentication
The access token from the `/login` request must be provided as a Bearer token

#### Example Response
```json
{
    "error": false,
    "accessGranted": true,
    "menus": [
        {
            "id": "90945",
            "name": "The New School",
            "showPrices": false,
            "menuFirstDate": "08/13/2019",
            "schoolId": "1370",
            "cycleLength": "16",
            "lastUpdate": "1564169917"
        }
    ]
}
```

The `menuFirstDate` is the first day food will be served, so in the example, week 0 is whatever week 2019-08-13 falls on.

`cycleLength` is the amount of weeks the menu runs for, so this menu has data for weeks 0-15

### `/checkMenuLastUpdate` (GET)
I'm not 100% on what this does, but as far as I can tell, it's an endpoint to see if the menu has updated since a certain time.

#### Query Args
* `menuId` (Number): A menu ID found in `/getmenus`
* `lastUpdate` (Number): A unix timestamp corresponding to the last time the menu was checked for updates

#### Authentication
The access token from the `/login` request must be provided as a Bearer token

#### Example Response
```json
{
  "error": false,
  "accessGranted": true,
  "menuUpdate": true,
  "newLastUpdate": "1564174080"
}
```

### `/dataPull` (GET)
Seems to be a way to test if the authentication token works. If logged in, returns basic account info

#### Authentication
The access token from the `/login` request must be provided as a Bearer token

#### Example Response
```json
{
  "error": false,
  "accessGranted": true,
  "id": "123456",
  "userName": "John Smith",
  "partyId": "123456",
  "userEmail": "example@example.com",
  "emailVerified": true,
  "userUsername": "example@example.com",
  "userProfileImagePath": null,
  "allowedAccess": true,
  "allergenProfile": null,
  "associationRequests": [],
  "recommendedItems": [],
  "favorites": [],
  "school": {
    "id": "1370",
    "label": "S0140",
    "shortName": "thenewschool",
    "name": "The New School",
    "isCollege": false,
    "displayName": "School",
    "hasOnlineOrdering": false,
    "hasPerformanceSpotlight": false,
    "city": "Fayetteville",
    "state": "AR",
    "zip": "72703",
    "nameLabel": "S0140",
    "address": "2514 New School Place\\nFayetteville, AR 72703",
    "logoPath": "\/intranet\/images\/content\/logos0140.png",
    "contacts": [
      {
        "name": "Bobby Howe",
        "businessTitle": "District Manager",
        "phoneNumber": "4795217037",
        "emailAddress": "bhowe@sagedining.com",
        "employeePhotoPath": "\/intranet\/images\/employees\/bhowe.jpg"
      }
    ]
  }
}
```

### `/getmenuitems` (POST)
Pass in a week, and get food served that week

Instead of a date based (EX: 2019-08-12), this API uses a week/date system. So, the week in which `menuFirstDate` param found in `/getmenus` falls, is the 0th week. The week after that is week 1, and so on.

Sunday is day 0, Monday is day 1, etc, and Saturday is day 6.

#### JSON Params
* `id` (Number): A menu id found in `/getmenus`
* `week` (Number): Which week to get menu data for
* `day` (Number) (Optional): The day of the week to request menu data for. Appears to be optional, as omitting this parameter has no effect.
* `lastUpdate` (Number) (Optional): I'm not sure what this is for, but appears to have connection to values found in `/checkMenuLastUpdate`. Omitting this parameter had no effect.

#### Example Response
```json
{
  "error": false,
  "items": [
    {
      "id": "294260406",
      "menuId": "90945",
      "recipeId": "127972",
      "day": "1",
      "week": "0",
      "meal": "1",
      "station": "0",
      "card": "0",
      "name": "Corn Chowder",
      "desc": "",
      "price": "0.00",
      "dot": 2,
      "featured": false,
      "rating": -1,
      "popular": true,
      "allergens": [
        {
          "id": "41"
        },
        {
          "id": "161"
        },
        {
          "id": "611"
        },
        {
          "id": "999999"
        }
      ],
      "compositeItem": false
    },
    ...
  ]
}
```

Each menu item features a variety of data, including `date` and `week`, so you can put a real date on it.

Each item has a `meal` item, with a value corresponding to the following

0. Breakfast
1. Lunch
2. Dinner

Each item also has a `station` item, which the app uses to group similar items together with a header. Each value corresponds to a following header.

0. Stock Exchange
1. Improvisations
2. Classic Cuts Deli
3. Main Ingredient
4. Seasonings Seasonings
5. Crossroads
6. Mangia! Mangia!
7. Transit Fare
8. P.S.
9. Splashes
15. FreeStyle