using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Windows.Forms;

namespace SchedulerUI
{
    public partial class Form1 : Form
    {
        private Button? btnRun;
        private Label? lblTitle;
        private Label? lblSubtitle;
        private Label? lblStatus;

        public Form1()
        {
            InitializeComponent();
            BuildUI();
        }

        private void BuildUI()
        {
            this.Text = "Semester Scheduling Generator";
            this.StartPosition = FormStartPosition.CenterScreen;
            this.Size = new Size(700, 420);
            this.MinimumSize = new Size(700, 420);
            this.BackColor = Color.FromArgb(243, 247, 252);
            this.FormBorderStyle = FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;

            lblTitle = new Label();
            lblTitle.Text = "Semester Scheduling Generator";
            lblTitle.Font = new Font("Segoe UI", 22, FontStyle.Bold);
            lblTitle.ForeColor = Color.FromArgb(25, 55, 109);
            lblTitle.AutoSize = true;
            lblTitle.BackColor = Color.Transparent;
            this.Controls.Add(lblTitle);

            lblSubtitle = new Label();
            lblSubtitle.Text = "Click the button below to run the full scheduling process";
            lblSubtitle.Font = new Font("Segoe UI", 10, FontStyle.Regular);
            lblSubtitle.ForeColor = Color.FromArgb(90, 100, 120);
            lblSubtitle.AutoSize = true;
            lblSubtitle.BackColor = Color.Transparent;
            this.Controls.Add(lblSubtitle);

            btnRun = new Button();
            btnRun.Text = "Generate Schedule";
            btnRun.Font = new Font("Segoe UI", 12, FontStyle.Bold);
            btnRun.Size = new Size(240, 60);
            btnRun.BackColor = Color.FromArgb(0, 102, 204);
            btnRun.ForeColor = Color.White;
            btnRun.FlatStyle = FlatStyle.Flat;
            btnRun.FlatAppearance.BorderSize = 0;
            btnRun.Cursor = Cursors.Hand;
            btnRun.Click += BtnRun_Click;
            this.Controls.Add(btnRun);

            lblStatus = new Label();
            lblStatus.Text = "Ready";
            lblStatus.Font = new Font("Segoe UI", 10, FontStyle.Italic);
            lblStatus.ForeColor = Color.FromArgb(80, 80, 80);
            lblStatus.AutoSize = true;
            lblStatus.BackColor = Color.Transparent;
            this.Controls.Add(lblStatus);

            CenterControls();

            this.Resize += (s, e) => CenterControls();
            btnRun.MouseEnter += (s, e) => btnRun.BackColor = Color.FromArgb(0, 86, 172);
            btnRun.MouseLeave += (s, e) => btnRun.BackColor = Color.FromArgb(0, 102, 204);
        }

        private void CenterControls()
        {
            if (lblTitle != null)
                lblTitle.Location = new Point((this.ClientSize.Width - lblTitle.Width) / 2, 60);

            if (lblSubtitle != null)
                lblSubtitle.Location = new Point((this.ClientSize.Width - lblSubtitle.Width) / 2, 115);

            if (btnRun != null)
                btnRun.Location = new Point((this.ClientSize.Width - btnRun.Width) / 2, 180);

            if (lblStatus != null)
                lblStatus.Location = new Point((this.ClientSize.Width - lblStatus.Width) / 2, 270);
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);

            using (var brush = new System.Drawing.Drawing2D.LinearGradientBrush(
                this.ClientRectangle,
                Color.FromArgb(243, 247, 252),
                Color.FromArgb(225, 235, 248),
                90f))
            {
                e.Graphics.FillRectangle(brush, this.ClientRectangle);
            }
        }

        private async void BtnRun_Click(object? sender, EventArgs e)
        {
            try
            {
                if (btnRun != null)
                {
                    btnRun.Enabled = false;
                    btnRun.Text = "Processing...";
                }

                if (lblStatus != null)
                    lblStatus.Text = "Running ETL and scheduling system...";

                CenterControls();

                string pythonPath = "python";

                // عدل هذا المسار حسب مكان main.py الحقيقي عندك
                string scriptPath = @"C:\Users\User\Desktop\ssg\main.py";

                ProcessStartInfo start = new ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = $"\"{scriptPath}\"",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                using (Process process = new Process())
                {
                    process.StartInfo = start;
                    process.Start();

                    string output = await process.StandardOutput.ReadToEndAsync();
                    string error = await process.StandardError.ReadToEndAsync();
                    process.WaitForExit();

                    if (process.ExitCode == 0 && string.IsNullOrWhiteSpace(error))
                    {
                        if (lblStatus != null)
                            lblStatus.Text = "Schedule generated successfully.";

                        CenterControls();

                        string pdfPath = Path.Combine(
                            Path.GetDirectoryName(scriptPath) ?? "",
                            "semester_schedule.pdf"
                        );

                        MessageBox.Show(
                            "Schedule generated successfully.",
                            "Success",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Information
                        );

                        if (File.Exists(pdfPath))
                        {
                            Process.Start(new ProcessStartInfo
                            {
                                FileName = pdfPath,
                                UseShellExecute = true
                            });
                        }
                    }
                    else
                    {
                        if (lblStatus != null)
                            lblStatus.Text = "An error occurred أثناء التشغيل.";

                        CenterControls();

                        MessageBox.Show(
                            "Error while running the project:\n\n" + error + "\n\nOutput:\n" + output,
                            "Execution Error",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Error
                        );
                    }
                }
            }
            catch (Exception ex)
            {
                if (lblStatus != null)
                    lblStatus.Text = "Unexpected error.";

                CenterControls();

                MessageBox.Show(
                    "Unexpected error:\n\n" + ex.Message,
                    "Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
            }
            finally
            {
                if (btnRun != null)
                {
                    btnRun.Enabled = true;
                    btnRun.Text = "Generate Schedule";
                }

                CenterControls();
            }
        }
    }
}