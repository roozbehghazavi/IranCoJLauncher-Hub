TraceDef()
{
	LifeTime()
	{
		keyf(0, 35)
	}

	Size()
	{
		randf(0, 25, 45)
	}

	MaxNumTraces(160)

	Color()
	{
		keyv4(0, 1, 1, 1, 0)
		keyv4(0.4, 1, 1, 1, 1)
		keyv4(25, 1, 1, 1, 1)
		keyv4(35, 1, 1, 1, 0)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_BloodPool_trace.mat")

	TexPlayMode("random_once", 0)
	TexMultiRect(2, 2, 0, 0)
}
