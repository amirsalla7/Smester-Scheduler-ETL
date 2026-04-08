using System;
using System.Collections.Generic;
using System.Windows.Forms;

namespace SchedulerUI
{
    public partial class LoginForm : Form
    {
        private Dictionary<string, string> users = new Dictionary<string, string>()
        {
            { "admin", "1234" },
            { "amir", "2026" },
            { "user", "pass" }
        };

        TextBox txtUser;
        TextBox txtPass;
        Button btnLogin;

        public LoginForm()
        {
            BuildUI();
        }

        private void BuildUI()
        {
            this.Text = "Login";
            this.Width = 350;
            this.Height = 220;
            this.StartPosition = FormStartPosition.CenterScreen;

            Label lblUser = new Label();
            lblUser.Text = "Username";
            lblUser.Top = 20;
            lblUser.Left = 30;
            lblUser.Width = 80;

            txtUser = new TextBox();
            txtUser.Top = 40;
            txtUser.Left = 30;
            txtUser.Width = 250;

            Label lblPass = new Label();
            lblPass.Text = "Password";
            lblPass.Top = 70;
            lblPass.Left = 30;
            lblPass.Width = 80;

            txtPass = new TextBox();
            txtPass.Top = 90;
            txtPass.Left = 30;
            txtPass.Width = 250;
            txtPass.PasswordChar = '*';

            btnLogin = new Button();
            btnLogin.Text = "Login";
            btnLogin.Top = 130;
            btnLogin.Left = 30;
            btnLogin.Width = 250;
            btnLogin.Height = 35;
            btnLogin.Click += BtnLogin_Click;

            this.Controls.Add(lblUser);
            this.Controls.Add(txtUser);
            this.Controls.Add(lblPass);
            this.Controls.Add(txtPass);
            this.Controls.Add(btnLogin);
        }

        private void BtnLogin_Click(object sender, EventArgs e)
        {
            string username = txtUser.Text.Trim();
            string password = txtPass.Text.Trim();

            if (users.ContainsKey(username) && users[username] == password)
            {
                Form1 main = new Form1();
                main.Show();
                this.Hide();
            }
            else
            {
                MessageBox.Show(
                    "Wrong username or password",
                    "Login Failed",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
            }
        }
    }
}