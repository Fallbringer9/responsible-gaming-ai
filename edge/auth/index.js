const crypto = require("crypto");
const https = require("https");
const querystring = require("querystring");

const COGNITO_DOMAIN =
    "responsible-gaming-operator-dev.auth.eu-west-3.amazoncognito.com";

const CLIENT_ID = "13qk04nkrp1bfgedh8q79uhlbg";

const CALLBACK_URL =
    "https://responsible-gaming.manuworld.fr/auth/callback";

const LOGOUT_URL =
    "https://responsible-gaming.manuworld.fr/";

const COOKIE_DOMAIN = "responsible-gaming.manuworld.fr";

const SCOPES = "openid email profile";

const ACCESS_TOKEN_COOKIE = "rg_access_token";
const STATE_COOKIE = "rg_oauth_state";
const VERIFIER_COOKIE = "rg_pkce_verifier";


exports.handler = async (event) => {
    const request = event.Records[0].cf.request;

    const uri = request.uri;
    const cookies = parseCookies(request.headers.cookie);

    if (uri === "/auth/logout") {
        return handleLogout();
    }

    if (uri === "/auth/callback") {
        return handleCallback(request, cookies);
    }

    const accessToken = cookies[ACCESS_TOKEN_COOKIE];

    if (!accessToken) {
        return startAuthentication();
    }

    if (uri.startsWith("/api/")) {
        request.headers.authorization = [
            {
                key: "Authorization",
                value: `Bearer ${accessToken}`,
            },
        ];

        request.uri = uri.slice(4);
    }

    return request;
};


function handleLogout() {
    const cognitoLogoutUrl =
        `https://${COGNITO_DOMAIN}/logout?` +
        querystring.stringify({
            client_id: CLIENT_ID,
            logout_uri: LOGOUT_URL,
        });

    return {
        status: "302",
        statusDescription: "Found",

        headers: {
            location: [
                {
                    key: "Location",
                    value: cognitoLogoutUrl,
                },
            ],

            "set-cookie": [
                {
                    key: "Set-Cookie",
                    value: deleteCookie(ACCESS_TOKEN_COOKIE),
                },
                {
                    key: "Set-Cookie",
                    value: deleteCookie(STATE_COOKIE),
                },
                {
                    key: "Set-Cookie",
                    value: deleteCookie(VERIFIER_COOKIE),
                },
            ],

            "cache-control": [
                {
                    key: "Cache-Control",
                    value: "no-store",
                },
            ],
        },
    };
}


function startAuthentication() {
    const state = randomBase64Url(32);
    const verifier = randomBase64Url(64);

    const challenge = crypto
        .createHash("sha256")
        .update(verifier)
        .digest("base64url");

    const authorizeUrl =
        `https://${COGNITO_DOMAIN}/oauth2/authorize?` +
        querystring.stringify({
            response_type: "code",
            client_id: CLIENT_ID,
            redirect_uri: CALLBACK_URL,
            scope: SCOPES,
            state,
            code_challenge_method: "S256",
            code_challenge: challenge,
        });

    return {
        status: "302",
        statusDescription: "Found",

        headers: {
            location: [
                {
                    key: "Location",
                    value: authorizeUrl,
                },
            ],

            "set-cookie": [
                {
                    key: "Set-Cookie",
                    value: buildCookie(
                        STATE_COOKIE,
                        state,
                        300,
                        true
                    ),
                },
                {
                    key: "Set-Cookie",
                    value: buildCookie(
                        VERIFIER_COOKIE,
                        verifier,
                        300,
                        true
                    ),
                },
            ],

            "cache-control": [
                {
                    key: "Cache-Control",
                    value: "no-store",
                },
            ],
        },
    };
}


async function handleCallback(request, cookies) {
    const params = new URLSearchParams(request.querystring);

    const code = params.get("code");
    const returnedState = params.get("state");

    const expectedState = cookies[STATE_COOKIE];
    const verifier = cookies[VERIFIER_COOKIE];

    if (!code || !returnedState || !expectedState || !verifier) {
        return errorResponse("Invalid OAuth callback.");
    }

    if (!safeEqual(returnedState, expectedState)) {
        return errorResponse("Invalid OAuth state.");
    }

    try {
        const tokens = await exchangeCodeForTokens(code, verifier);

        if (!tokens.access_token) {
            return errorResponse(
                "Cognito did not return an access token."
            );
        }

        return {
            status: "302",
            statusDescription: "Found",

            headers: {
                location: [
                    {
                        key: "Location",
                        value: "/",
                    },
                ],

                "set-cookie": [
                    {
                        key: "Set-Cookie",
                        value: buildCookie(
                            ACCESS_TOKEN_COOKIE,
                            tokens.access_token,
                            tokens.expires_in || 3600,
                            true
                        ),
                    },
                    {
                        key: "Set-Cookie",
                        value: deleteCookie(STATE_COOKIE),
                    },
                    {
                        key: "Set-Cookie",
                        value: deleteCookie(VERIFIER_COOKIE),
                    },
                ],

                "cache-control": [
                    {
                        key: "Cache-Control",
                        value: "no-store",
                    },
                ],
            },
        };
    } catch (error) {
        console.error(
            "OAuth token exchange failed:",
            error.message
        );

        return errorResponse("Authentication failed.");
    }
}


function exchangeCodeForTokens(code, verifier) {
    const body = querystring.stringify({
        grant_type: "authorization_code",
        client_id: CLIENT_ID,
        code,
        redirect_uri: CALLBACK_URL,
        code_verifier: verifier,
    });

    const options = {
        hostname: COGNITO_DOMAIN,
        path: "/oauth2/token",
        method: "POST",

        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": Buffer.byteLength(body),
        },
    };

    return new Promise((resolve, reject) => {
        const req = https.request(options, (res) => {
            let responseBody = "";

            res.on("data", (chunk) => {
                responseBody += chunk;
            });

            res.on("end", () => {
                if (
                    res.statusCode < 200 ||
                    res.statusCode >= 300
                ) {
                    reject(
                        new Error(
                            `Cognito token endpoint returned ${res.statusCode}`
                        )
                    );

                    return;
                }

                try {
                    resolve(JSON.parse(responseBody));
                } catch {
                    reject(
                        new Error(
                            "Invalid JSON returned by Cognito."
                        )
                    );
                }
            });
        });

        req.on("error", reject);

        req.write(body);
        req.end();
    });
}


function parseCookies(cookieHeaders = []) {
    const cookies = {};

    for (const header of cookieHeaders) {
        const parts = header.value.split(";");

        for (const part of parts) {
            const separatorIndex = part.indexOf("=");

            if (separatorIndex === -1) {
                continue;
            }

            const name = part
                .slice(0, separatorIndex)
                .trim();

            const value = part
                .slice(separatorIndex + 1)
                .trim();

            cookies[name] = value;
        }
    }

    return cookies;
}


function buildCookie(name, value, maxAge, httpOnly) {
    const attributes = [
        `${name}=${value}`,
        "Path=/",
        `Domain=${COOKIE_DOMAIN}`,
        `Max-Age=${maxAge}`,
        "Secure",
        "SameSite=Lax",
    ];

    if (httpOnly) {
        attributes.push("HttpOnly");
    }

    return attributes.join("; ");
}


function deleteCookie(name) {
    return [
        `${name}=`,
        "Path=/",
        `Domain=${COOKIE_DOMAIN}`,
        "Max-Age=0",
        "Secure",
        "HttpOnly",
        "SameSite=Lax",
    ].join("; ");
}


function randomBase64Url(bytes) {
    return crypto
        .randomBytes(bytes)
        .toString("base64url");
}


function safeEqual(left, right) {
    const leftBuffer = Buffer.from(left);
    const rightBuffer = Buffer.from(right);

    if (leftBuffer.length !== rightBuffer.length) {
        return false;
    }

    return crypto.timingSafeEqual(
        leftBuffer,
        rightBuffer
    );
}


function errorResponse(message) {
    return {
        status: "401",
        statusDescription: "Unauthorized",

        headers: {
            "content-type": [
                {
                    key: "Content-Type",
                    value: "text/plain; charset=utf-8",
                },
            ],

            "cache-control": [
                {
                    key: "Cache-Control",
                    value: "no-store",
                },
            ],
        },

        body: message,
    };
}
