TraceDef()
{
	LifeTime()
	{
		keyf(0, 30)
	}

	Size()
	{
		randf(0, 4, 9)
	}

	MaxNumTraces(300)

	Color()
	{
		keyv4(0, 1, 1, 1, 0)
		keyv4(0.25, 1, 1, 1, 1)
		keyv4(22, 1, 1, 1, 1)
		keyv4(30, 1, 1, 1, 0)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_BloodDripSplat_trace.mat")

	TexPlayMode("random_once", 0)
	TexMultiRect(2, 2, 0, 0)
}
