document.addEventListener("DOMContentLoaded", function () {
    const path = window.location.pathname;
    if (path.startsWith("/fa/")) {
      document.documentElement.setAttribute("dir", "rtl");
      document.documentElement.setAttribute("lang", "fa");
      document.body.setAttribute("dir", "rtl");
    } else {
        document.documentElement.setAttribute("dir", "ltr");
        document.documentElement.setAttribute("lang", "en");
        document.body.setAttribute("dir", "ltr");
    }
  });
