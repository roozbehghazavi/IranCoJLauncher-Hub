TraceDef()
{
	LifeTime()
	{
		keyf(0, 40)
	}

	Size()
	{
		randf(0, 40, 90)
	}

	MaxNumTraces(60)

	Color()
	{
		keyv4(0, 1, 1, 1, 1)
		keyv4(30, 1, 1, 1, 1)
		keyv4(40, 1, 1, 1, 0)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_BloodSplat_trace.mat")

	TexPlayMode("random_once", 0)
	TexMultiRect(2, 2, 0, 0)
}
