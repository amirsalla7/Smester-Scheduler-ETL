using System;
using System.Windows.Forms;
using Microsoft.VisualBasic.Logging;

namespace SchedulerUI
{
    internal static class Program
    {
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new LoginForm());
        }
    }
}