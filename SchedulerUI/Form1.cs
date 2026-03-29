using System;
using System.Diagnostics;
using System.Windows.Forms;

namespace SchedulerUI
{
    public partial class Form1 : Form
    {
        Button btnRun;

        public Form1()
        {
            InitializeComponent();
            CreateButton();
        }

        private void CreateButton()
        {
            btnRun = new Button();

            btnRun.Text = "Generate Schedule";

            btnRun.Width = 200;

            btnRun.Height = 50;

            btnRun.Top = 60;

            btnRun.Left = 80;

            btnRun.Click += BtnRun_Click;

            Controls.Add(btnRun);
        }

        private void BtnRun_Click(object sender, EventArgs e)
        {
            try
            {
                ProcessStartInfo start = new ProcessStartInfo();

                start.FileName = "python";

                start.Arguments = @"C:\Users\User\Desktop\ssg\main.py";

                start.UseShellExecute = false;

                start.RedirectStandardOutput = true;

                start.RedirectStandardError = true;

                start.CreateNoWindow = true;

                Process process = Process.Start(start);

                string output = process.StandardOutput.ReadToEnd();

                string error = process.StandardError.ReadToEnd();

                process.WaitForExit();

                if (string.IsNullOrEmpty(error))
                {
                    MessageBox.Show("Schedule generated successfully");
                }
                else
                {
                    MessageBox.Show(error);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }
    }
}