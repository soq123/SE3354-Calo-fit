using DietRoutine.Api.Models;
using Microsoft.EntityFrameworkCore;

namespace DietRoutine.Api.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<FoodItem> FoodItems => Set<FoodItem>();
    public DbSet<LogEntry> LogEntries => Set<LogEntry>();
}
