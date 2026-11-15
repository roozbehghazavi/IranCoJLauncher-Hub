TraceDef()
{
	LifeTime()
	{
		keyf(0, 45)
	}

	Size()
	{
		randf(0, 35, 60)
	}

	MaxNumTraces(120)

	Color()
	{
		keyv4(0, 1, 1, 1, 0)
		keyv4(0.6, 1, 1, 1, 1)
		keyv4(33, 1, 1, 1, 1)
		keyv4(45, 1, 1, 1, 0)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Material("IRN_BloodPool_trace.mat")

	TexPlayMode("random_once", 0)
	TexMultiRect(2, 2, 0, 0)
}
