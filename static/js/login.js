window.onload = function () {
  sign_in = document.getElementById('signin');
  form = document.getElementById('myform');
  sign_in.onclick = function () {
    form.action = "/login"
  }
}