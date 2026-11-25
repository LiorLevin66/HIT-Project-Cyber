// Marks each password requirement with a check while the user types.
// This is only for the user - the server checks all the rules again.
var list = document.getElementById("password-rules");
var password = document.getElementById("password");
var confirmPassword = document.getElementById("confirm");

function checkRules() {
    var value = password.value;
    var rules = {
        length: value.length >= parseInt(list.dataset.min),
        upper: /[A-Z]/.test(value),
        lower: /[a-z]/.test(value),
        digit: /[0-9]/.test(value),
        special: /[!-\/:-@\[-`{-~]/.test(value),
        match: value.length > 0 && value === confirmPassword.value
    };

    var items = list.getElementsByTagName("li");
    for (var i = 0; i < items.length; i++) {
        var rule = items[i].getAttribute("data-rule");
        if (rules[rule]) {
            items[i].className = "ok";
        } else {
            items[i].className = "";
        }
    }
}

if (list && password && confirmPassword) {
    password.addEventListener("input", checkRules);
    confirmPassword.addEventListener("input", checkRules);
}
