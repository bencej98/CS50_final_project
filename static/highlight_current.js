
// Gets each elements href
home_href = document.getElementById("home").href
transactions_href = document.getElementById("transactions").href
budget_href = document.getElementById("budget").href
reports_href = document.getElementById("reports").href
admin_href = document.getElementById("admin").href



// Comapres the current href with the elements href and adds active class on the current one
if (window.location.href == home_href) { 
    document.getElementById("home").classList.add("nav-link","active");
} else if (window.location.href == transactions_href) {
    document.getElementById("transactions").classList.add("nav-link","active");
} else if (window.location.href == budget_href) {
    document.getElementById("budget").classList.add("nav-link","active");
} else if (window.location.href == reports_href) {
    document.getElementById("reports").classList.add("nav-link","active");
} else if (window.location.href == admin_href) {
    document.getElementById("admin").classList.add("nav-link","active");
}

// This is hard coded, must be a better solution for this