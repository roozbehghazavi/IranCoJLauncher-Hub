TraceDef()
{
	LifeTime()
	{
		keyf(0, 25)
	}

	Size()
	{
		randf(0, 16, 40)
	}

	MaxNumTraces(160)

	Color()
	{
		keyv4(0, 1, 1, 1, 1)
		keyv4(17, 1, 1, 1, 1)
		keyv4(25, 1, 1, 1, 0)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_BloodSplat_trace.mat")

	TexPlayMode("random_once", 0)
	TexMultiRect(2, 2, 0, 0)
}
