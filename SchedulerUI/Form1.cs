using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace SchedulerUI
{
    public partial class Form1 : Form
    {
        private Button? btnRun;
        private Label? lblTitle;
        private Label? lblSubtitle;
        private Label? lblStatus;
        private ProgressBar? progressBar;

        public Form1()
        {
            InitializeComponent();
            BuildUI();
        }

        private void BuildUI()
        {
            this.Text = "Semester Scheduling Generator";
            this.StartPosition = FormStartPosition.CenterScreen;
            this.Size = new Size(720, 460);
            this.MinimumSize = new Size(720, 460);
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

            progressBar = new ProgressBar();
            progressBar.Size = new Size(420, 24);
            progressBar.Minimum = 0;
            progressBar.Maximum = 100;
            progressBar.Value = 0;
            progressBar.Style = ProgressBarStyle.Continuous;
            this.Controls.Add(progressBar);

            lblStatus = new Label();
            lblStatus.Text = "Ready";
            lblStatus.Font = new Font("Segoe UI", 10, FontStyle.Italic);
            lblStatus.ForeColor = Color.FromArgb(80, 80, 80);
            lblStatus.AutoSize = true;
            lblStatus.BackColor = Color.Transparent;
            this.Controls.Add(lblStatus);

            CenterControls();

            this.Resize += (s, e) => CenterControls();

            btnRun.MouseEnter += (s, e) =>
            {
                if (btnRun.Enabled)
                    btnRun.BackColor = Color.FromArgb(0, 86, 172);
            };

            btnRun.MouseLeave += (s, e) =>
            {
                if (btnRun.Enabled)
                    btnRun.BackColor = Color.FromArgb(0, 102, 204);
            };
        }

        private void CenterControls()
        {
            if (lblTitle != null)
                lblTitle.Location = new Point((this.ClientSize.Width - lblTitle.Width) / 2, 55);

            if (lblSubtitle != null)
                lblSubtitle.Location = new Point((this.ClientSize.Width - lblSubtitle.Width) / 2, 110);

            if (btnRun != null)
                btnRun.Location = new Point((this.ClientSize.Width - btnRun.Width) / 2, 170);

            if (progressBar != null)
                progressBar.Location = new Point((this.ClientSize.Width - progressBar.Width) / 2, 255);

            if (lblStatus != null)
                lblStatus.Location = new Point((this.ClientSize.Width - lblStatus.Width) / 2, 295);
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

        private void UpdateProgress(int value, string statusText)
        {
            if (progressBar != null)
            {
                int safeValue = Math.Max(progressBar.Minimum, Math.Min(progressBar.Maximum, value));
                progressBar.Value = safeValue;
            }

            if (lblStatus != null)
                lblStatus.Text = statusText;

            CenterControls();
            Application.DoEvents();
        }

        private async Task FakeProgressAsync()
        {
            UpdateProgress(5, "Starting system...");
            await Task.Delay(250);

            UpdateProgress(15, "Loading data...");
            await Task.Delay(300);

            UpdateProgress(30, "Analyzing students...");
            await Task.Delay(300);

            UpdateProgress(45, "Building course offering...");
            await Task.Delay(300);

            UpdateProgress(60, "Generating schedule...");
            await Task.Delay(400);

            UpdateProgress(80, "Saving schedule and exporting PDF...");
            await Task.Delay(400);
        }

        private async void BtnRun_Click(object? sender, EventArgs e)
        {
            try
            {
                if (btnRun != null)
                {
                    btnRun.Enabled = false;
                    btnRun.Text = "Processing...";
                    btnRun.BackColor = Color.FromArgb(120, 120, 120);
                }

                UpdateProgress(0, "Preparing execution...");

                string pythonPath = @"C:\Users\User\Desktop\ssg\.venv\Scripts\python.exe";
                string scriptPath = @"C:\Users\User\Desktop\ssg\main.py";
                string projectDir = Path.GetDirectoryName(scriptPath) ?? @"C:\Users\User\Desktop\ssg";
                string pdfPath = Path.Combine(projectDir, "semester_schedule.pdf");

                if (!File.Exists(pythonPath))
                    throw new FileNotFoundException("Python executable not found.", pythonPath);

                if (!File.Exists(scriptPath))
                    throw new FileNotFoundException("main.py not found.", scriptPath);

                ProcessStartInfo start = new ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = $"\"{scriptPath}\"",
                    WorkingDirectory = projectDir,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                using (Process process = new Process())
                {
                    process.StartInfo = start;
                    process.Start();

                    Task progressTask = FakeProgressAsync();

                    string output = await process.StandardOutput.ReadToEndAsync();
                    string error = await process.StandardError.ReadToEndAsync();

                    process.WaitForExit();
                    await progressTask;

                    if (process.ExitCode == 0 && string.IsNullOrWhiteSpace(error))
                    {
                        UpdateProgress(100, "Schedule generated successfully.");

                        if (!File.Exists(pdfPath))
                        {
                            MessageBox.Show(
                                "The process finished successfully, but the PDF file was not found.\n\n" +
                                "Expected file:\n" + pdfPath + "\n\nOutput:\n" + output,
                                "PDF Not Found",
                                MessageBoxButtons.OK,
                                MessageBoxIcon.Warning
                            );
                            return;
                        }

                        MessageBox.Show(
                            "Schedule generated and saved successfully.",
                            "Success",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Information
                        );

                        Process.Start(new ProcessStartInfo
                        {
                            FileName = pdfPath,
                            UseShellExecute = true
                        });
                    }
                    else
                    {
                        UpdateProgress(0, "Execution failed.");

                        MessageBox.Show(
                            "Error while running the project:\n\n" +
                            error +
                            "\n\nOutput:\n" +
                            output,
                            "Execution Error",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Error
                        );
                    }
                }
            }
            catch (Exception ex)
            {
                UpdateProgress(0, "Unexpected error.");

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
                    btnRun.BackColor = Color.FromArgb(0, 102, 204);
                }

                CenterControls();
            }
        }
    }
}